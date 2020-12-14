# batyam

a service that monitors and tracks updates regarding CC on different remote repositories projects in order to improve and streamline the code-review process, and bridge the differences across different code-review platforms.

[A report example on Google sheets](https://docs.google.com/spreadsheets/d/1GnxBXyfkdh8bE7n2r5URJyFJ3kD_yfwnkHHXNf09_v4/edit?urp=gmail_link)

## Terms & Concepts

- Code changes (CC):
    - logically complete pieces of code, such as feature, task, bug fix, improvement, etc. - which support one effort. 
    - AKA: Patch (gerrit), Merge request (GitLab), Pull request (Github). 
- Code Review (CR) - Humanized review (by reviewers) of a CC. 

## Personas

- Code Contributor. 
- Code Reviewer. 

## Challenges

1. CR process is not prioritized, which leads to a decline of incentive to perform CR.
2. CC not reviewed in a timely manner
3. Code contributors have a need to “pock” code reviewers (in-person/mail/IRC/gchat) in order to get their CC reviewed.
4. Complexity:
    - Multiple servers: GitHub, GitLab, gerrit.
    - Multiple hosts per server.
    - Multiple namespaces.
5. Lack of unified processes due to the complexity.
6. It’s not clear who is able to do a CR for each repository.
7. CR efforts are not tracked and managed.
8. Code Reviewers are not aware which CC ought to be reviewed/re-reviewed
    - Not all services have a re-review functionality.
    - There is a ‘ping-pong’ between the contributor and the reviewer.
9. Unclear/ inconsistent when a CC is in a ready to merge status.
10. No policy for conflicts resolution.
11. No specific order in CR for CC.

# MVP

- A containerized service running on Openshift (PSI), running a python application triggered automatically, once a day. 
- Service will pull information from the related namespaces on git servers regarding currently open CC in the form of an aggregated report. 
- Send the report as an email to the relevant code reviewers. 
- Tested using the pytest framework. 

## Success Criteria

Improved visibility of current CC’s. 

# Requirements

- Copy the .env_template file content to a .env file and insert the required keys.
