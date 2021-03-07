#!/usr/bin/env python3

from dotenv import load_dotenv

load_dotenv()  # loaded here so imports will have access to the env variables
import smtplib
from email.message import EmailMessage
import pandas as pd
import base
import yaml
import logging
import requests
import json
import google_spreadsheets
import os
from datetime import datetime

logging.basicConfig(filename='report.log',
                    level=logging.INFO,
                    format="%(asctime)s; %(levelname)s: %(message)s",
                    datefmt='%d/%m/%Y',
                    )


def send_email(subject, body, recipients=None):
    """send an email to the selected recipients with a given body context."""

    # TODO: hack for now, validation should happen when program starts
    email_from = os.getenv("EMAIL_FROM")
    if not email_from:
        logging.info("no EMAIL_FROM env var set, exiting")
        raise Exception()

    if recipients:
        msg = EmailMessage()
        msg['Subject'] = f'{subject} - {datetime.now().date().strftime("%d/%m/%y")}'
        msg['From'] = email_from
        msg['To'] = ", ".join(recipients)
        msg.set_content(body, subtype='html')
        # the localhost assumes you have an smtp server running on you machine
        with smtplib.SMTP(os.getenv("EMAIL_PROXY_SERVER", "localhost")) as server:
            server.send_message(msg)
            logging.info("mail sent successfully.")
    else:
        logging.info("No recipients given, Mail not sent.")


def publish(report, recipients=None, team=None):
    """Outputs the report to Google sheets and publish it as a mail"""
    title = f"Open Code Contributions - {team}"
    if report.empty:
        body = report.to_html(justify='left')
        logging.info("Sending an empty report.")
    else:
        google_sheet = google_spreadsheets.create_and_share_spreadsheet(title, report)
        body = f"<p>The report is also available on Google Sheets:<br> {google_sheet}</p> {report.to_html(justify='left')}"
    send_email(title, body, recipients)


def process(df_cc, servers):
    """fills a DF with the CC from each of the selected servers."""
    have_namespaces_or_users = False
    try:
        for server in servers:
            if server.namespaces or server.users:
                for cc in server.get_ccs():
                    code_change = server.cc_to_dict(cc)
                    df_cc = df_cc.append(code_change, ignore_index=True)
                have_namespaces_or_users = True
            else:
                logging.warning(f"No valid namespaces or users entered for the {server.name} server.")
    except TypeError as e:
        logging.warning(f"No servers or users entered: {e}.")
    if not have_namespaces_or_users:
        logging.warning("No valid namespaces or users entered overall.")
    return df_cc


def get_configuration():
    """reads a yaml config file and returns it's object."""
    config_dir = os.getenv('CONFIG_PATH', 'config.yaml')
    try:
        with open(config_dir, 'r') as stream:
            return yaml.load(stream, Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        logging.ERROR(f"Yaml file '{config_dir}' is not found: {e}.")
        raise e


def create_servers_from_dictionary(team):
    """reads a dictionary of servers configurations and creates a list of server objects per server in it."""
    servers = []
    try:
        for server in team.get('servers'):
            if server.get('vendor').casefold() == 'GitLab'.casefold():
                servers.append(base.Gitlab(server.get('host'), server.get('namespaces'), server.get('users'),
                                           server.get('repositories')))
            elif server.get('vendor').casefold() == 'GitHub'.casefold():
                servers.append(base.GitHub(server.get('host'), server.get('namespaces'), server.get('repositories')))
            else:
                servers.append(base.Gerrit(server.get('host'), server.get('bot_users'), server.get('repositories')))
    except (ValueError, TypeError) as e:
        logging.warning(f"No valid servers found: {e}.")
    return servers


def post_to_http(df):
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    formatted = json.dumps(parsed, indent=4)
    displayer_host = os.getenv('DISPLAYER_HOST', '127.0.0.1:8000')
    try:
        request = requests.post(f'http://{displayer_host}/database/update', data = formatted)
    except requests.exceptions.ConnectionError:
        print("Server is unreachable and probably down.")


def main():
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.max_columns', 10)
    frames = []
    for team in get_configuration().get('teams'):
        # produce a separate report for each team (recipient)

        logging.info(f'Producing report: {team.get("name")}')
        df_cc = pd.DataFrame(
            columns=['project', 'last updated', 'contributor', 'state', 'title', 'web_url']
        )
        server_list = create_servers_from_dictionary(team)
        df_cc = process(df_cc, server_list)
        df_cc.index += 1
        publish(df_cc, team.get('recipients'), team.get("name"))
        frames.append(df_cc)

    post_to_http(pd.concat(frames))


if __name__ == '__main__':
    main()
