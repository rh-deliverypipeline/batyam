This Documents will hold all information relevant for contributing to this repository

# ./deploy contribution
In order to contribute to `./deploy/` follow these steps

## Setup
Please setup your env with `ansible-vault` to a file under `./deploy/vaults/`

to do that use the command:
```
ansible-vault create ./deploy/vaults/dev/secret-vars.yml
```

the path needs to be under the `./deploy/vaults/` in order to not commit accidently your secret

a sample inventory file is shown in `./deploy/vaults/secret-vars-sample.yml`

and is exposed and has sample values for demonstration purposes.

## Testing
to test and deploy, run the command:
```
VAULT_PASSWORD_FILE=your/password/file.yml ./deploy/deploy.sh
```
which without any more fields, deploy the application to your `batyam_ocp_host`

## Conventions
In order to keep resources in a managed state, we created a few guidelines

### Put defaults when you can, and if you can't put them in ansible-vault
Each variable should have a sensible value if possible, and if one is not available, put it in the ansible-vault

### Prefix and suffix and label resources to provide a consitent view
In order to make each resource look consistent we made some standards for our reources

#### Start with 'batyam-'
That we can distinguish between then and other static resources that were previously created

#### End with '-volume'/ '-envvar'  for ConfigMaps and Secrets
To dintinguish between resources we mount and environment variables, and some we mount as files, we denoted this suffix

- -volume: for volumeMounts
- -envvar: for environment variables

## Format of `batyam_configs_repo`
As of now, the way this repo should look like is:
```
$ cd $batyam_configs_repo && find . -maxdepth 1
.
./config.yaml
./.git
```

where config.yaml should be in the general format of the [config.yaml file](./config.yaml)
