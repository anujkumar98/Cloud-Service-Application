# CSYE 6225 - Spring 2023 - webapp - A7 demo Changes
___

## Technology Stack
<ul>
<li>Backend Technology: Python</li>
<li>Framework: FastAPI </li>
<li>Database: MySQL </li>
</ul>

____

## Build Instructions

<ul> <li>Clone this repository </li> </ul>

```
$ git clone git@github.com:Anuj-Kumar-Networks-Cloud-CSYE6225/webapp.git
```
<ul> <li>Navigate to webapp directory </li> </ul>

```
$ cd webapp
```
<ul> <li>Run command on terminal to install all the required dependencies</li></ul>

```
pip install -r requirements.txt
```
___
## Deploy Instructions

<ul> <li>Create Enviornment File </li></ul>

```
HOST={HOST_NAME}
USERNAME={USERNAME}
PASSWORD={PASSWORD}
SCHEMA_NAME={SCHEMA_NAME}
USER_DATA_TABLE={TABLE_NAME}
PRODUCT_DATA_TABLE={TABLE_NAME}
```
<ul><li>Start application</li></ul>

```
$ python main.py
```

<ul><li>Test endpoints on Postman</li></ul>

___

## Run Test

<ul><li>To Run tests</li></ul>

```
$ python -m pytest --import-mode=append test/
```

## Run Packer File

<ul><li>Format Packer</li></ul>

```
$ packer fmt .
```

<ul><li>Validate the packer file</li></ul>

```
$ packer validate
```

<ul><li>Initialize Packer</li></ul>

```
$ packer init
```

<ul><li>Build Packer File</li></ul>

```
$ packer build -var-file={variables_file} packer_file.hcl
```

