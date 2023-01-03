# DellEMC Data Domain Ansible Collection

Ansible collection is used to get, create, modify or delete the Data Domain resources to automate the configuration tasks easy and fast.

## Pre-requisites

  - Python V3.8 or higher
  
## Installation of Ansible Collection

  Use below command to install the collection.

  `ansible-galaxy collection install git+https://github.com/dell/ansible-datadomain.git`

  Install all packages from the requirements.txt file
  
  `pip install -r pip install <collection-install-path>/dellemc/datadomain/requirements.txt`

## Inventory file

  Build the inventory file as below
  ```
  [dd]
  10.150.15.9

  [dd:vars]
  ansible_port = 22
  ansible_user = sysadmin
  private_key_file = /root/.ssh/id_rsa

  ```
  If you want to use user password instead of rsa login, use `ansible_ssh_pass` parameter to specify password and remove `private_key_file` parameter. e.g 
  
  ```
  [dd]
  10.150.15.9

  [dd:vars]
  ansible_port = 22
  ansible_user = sysadmin
  ansible_ssh_pass = 'password'

  ```
  
##  Ansible Playbook
To make the rest api call or ssh call from the host you are running the playbook; use below parameter at the top of the playbook

`connection: local`

## Sample Playbook

  ```
- name: Data Domain Playbook.
  hosts: dd
  connection: local
  gather_facts: false

  tasks:
    - name: Create Share
      dellemc.datadomain.cifs:
          state: create
          share: backup_share
          clients: '*'
          path: /backup
      register: status
    
    - debug:
        msg: "{{ status }}"
  ```
Documentation for the collection.

#Copyright ©️ 2022 Dell Inc. or its subsidiaries.
