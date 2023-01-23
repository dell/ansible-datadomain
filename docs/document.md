# Ansible Collection for Dell Technologies DataDomain
© 2022 Dell Inc. or its subsidiaries. All rights reserved. Dell and other trademarks are trademarks of Dell Inc. or its subsidiaries. Other trademarks may be trademarks of their respective owners.

## Contents
*   [adminaccess](#adminaccess)
*   [cifs](#cifs)
*   [compression](#compression)
*   [config](#config)
*   [ddboost](#ddboost)
*   [filesys](#filesys)
*   [mtree](#mtree)
*   [net](#net)
*   [nfs](#nfs)
*   [replication](#replication)
*   [users](#users)

--------------

# **adminaccess**

The adminaccess command manages access control and enables users enable/disable remote hosts to use the FTP, FTPS, Telnet, HTTP, HTTPS, SSH, and SCP administrative protocols on the protection system. 

## Supported Commands
-   adminaccess enable \<serviceName>
-   adminaccess disable \<serviceName>
-   adminaccess show

## Parameters
<style >
    
    table, td, th {text-align: center; border:1px solid black;}
    li {list-style-type:square; text-align: left;}
</style>

<table>
    <tr>
        <th colspan=1>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=1>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td> 
            <ul> 
                <li>enable</li>
                <li>disable</li>
                <li>show</li>
            </ul>
        </td>
        <td width="80%">State of the service you want to work with. Show will display all the services configuration.
        </td>
    </tr>
        <tr>
        <td colspan=1>service</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td> 
            <ul> 
                <li>http</li>
                <li>https</li>
                <li>ftp</li>
                <li>ftps</li>
                <li>telnet</li>
                <li>ssh</li>
                <li>scp</li>
                <li>web-service</li>
                <li>all</li>
            </ul>
        </td>
        <td width="80%">This attribute specifies the services you want to toggle      </td>
    </tr>
</table>


## Examples
```
- name: enable the https access on data domain
  dellemc.datadomain.adminaccess:
      state: enable
      service: https

- name: show attributes of all servies
  dellemc.datadomain.adminaccess:
      state: show
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

----------

# **cifs**
The cifs command manages CIFS data access between a protection system and Windows clients. Command options enable and disable access to a protection system from media servers and other Windows clients that use the CIFS protocol. The cifs command sets the authentication mode, share management, and administrative access, and displays status and statistics for CIFS clients.

## Supported Commands
  - cifs enable
  - cifs disable
  - cifs status
  - cifs share create
  - cifs share modify
  - cifs share enable
  - cifs share disable
  - cifs share destroy
  - cifs share show
  - cifs show config

## Parameters

<style >
    
    table, td, th {text-align: center; border:1px solid black;}
    li {list-style-type:square; text-align: left;}
</style>

<table>
    <tr>
        <th colspan=1>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=1>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td> 
            <ul> 
                <li>enable</li>
                <li>disable</li>
                <li>status</li>
                <li>destroy</li>
                <li>create</li>
                <li>show</li>
                <li>modify</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=1>share</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">A descriptive name for the share</td>
    </tr>
    <tr>
        <td colspan=1>path</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">The path to the target directory.</td>
    </tr>
    <tr>
        <td colspan=1>max-connections</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">The maximum number of connections to the share allowed at one time.</td>
    </tr>
    <tr>
        <td colspan=1>clients</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">A comma-separated list of clients allowed to access the share. Specify the clients by hostname or IP address. No spaces or tabs are allowed and the list must be enclosed in double quotes. If the clients argument is not specified when creating the share, the share is not cifs accessible by any client. To make the share accessible for all clients, enter the clients argument and precede client name by an ampersand.</td>
    </tr>
    <tr>
        <td colspan=1>users</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">A comma-separated list of user names. Other than the comma delimiter, spaces (blank or tab) are treated as part of the user name because a Windows user name can have a space in the name.
        The user names list can include group names. Group names must be preceded by the symbol for the word at (@).
        All users in the client list can access the share unless one or more user names are specified, in which case only the listed names can access the share. Separate group and user names by commas only. Spaces may be included within a group name but are not allowed as delimiters for group names.
</td>
    </tr>
    
</table>


## Examples
```
  - name: Disable CIFS
    dellemc.datadomain.cifs:
        state: disable

  - name: enable CIFS
    dellemc.datadomain.cifs:
        state: enable

  - name: Get CIFS status
    dellemc.datadomain.cifs:
        state: status

  - name: Create CIFS Share
    dellemc.datadomain.cifs:
        state: create
        share: share_ddfs
        path: /backup
        clients: '*'
  
  - name: Modify Share
    dellemc.datadomain.cifs:
        state: modify
        share: share_ddfs
        clients: '10.0.0.1'
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

----------

# **compression**
Physical capacity measurement (PCM) provides space usage information for a sub-set of storage space. You can view space usage information for MTrees, tenants, tenant units, and pathsets.

## Supported Commands
- compression schedule enable
- compression schedule disable
- compression status
- compression schedule destroy
- compression schedule modify
- compression schedule del
- compression schedule create
- compression schedule add
- compression sample stop
- compression sample start
- compression throttle set
- compression throttle show
- compression throttle reset

## Parameters

<style >
    
    table, td, th {text-align: center; border:1px solid black;}
    li {list-style-type:square; text-align: left;}
    td.elbow-placeholder {
        border-left: 1px solid #000;
        border-top: 0;
        border-bottom: 0;
        width: 10px;
        min-width: 10px;
    }
</style>

<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td> 
            <ul> 
                <li>enable</li>
                <li>disable</li>
                <li>status</li>
                <li>start</li>
                <li>stop</li>
                <li>add</li>
                <li>del</li>
                <li>create</li>
                <li>destroy</li>
                <li>modify</li>
                <li>set</li>
                <li>reset</li>
                <li>show</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
        <tr>
        <td colspan=2>sample</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">'Use this option to start/stop the PCM measurement sample</td>
    </tr>
        <tr>
        <td colspan=2>option</td>
        <td>dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">This parameter is a dictionary. Select from the below options</td>
    </tr>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>pathsets</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the pathset names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>tenants</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the tenants names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>tenants-units</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the tenants-units names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>mtrees</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the mtree names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>priority</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>normal</li>
                <li>urgent</li>
            </ul>
        </td>
         <td width="80%">Specify normal or urgent. Normal priority submits a measurement task to the processing queue. Urgent priority submits a measurement task to the front of the processing queue</td>
    </tr>
    </tr>
    <tr>
        <td colspan=2>initialize</td>
        <td>bool</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use this option when you want to enable and initialize the pcm.</td>
    </tr>
    <tr>
        <td colspan=2>schedule</td>
        <td>dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use this option to create, delete, enable, disable or destroy schedule</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Specify a schedule name</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>pathsets</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the pathset names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>pathsets</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the pathset names in list format</td>
    </tr>
        <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>tenants</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the tenants names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>tenants-units</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the tenants-units names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>mtrees</td>
        <td width="20%">list</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Type the mtree names in list format</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>priority</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>normal</li>
                <li>urgent</li>
            </ul>
        </td>
         <td width="80%">Select one of the priority to start the sample</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>time</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Specify the schedule start time in 24 hour format e.g. 13:00</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>day</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">With the keyword day, specify days as the days of the week using either lowercase, three letter abbreviations for the days of the week: mon, tue, wed, thu, fri, sat, sun, or as integers: 0 = Sunday, 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td> 
        <td colspan=1>monthly</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
         <td width="80%">Specify the days of the month using integers (1-31) and, optionally, use the word "last-day" to include the last day of every month in the year.</td>
    </tr>
    <tr>
        <td colspan=2>throttle</td>
        <td>str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify how much CPU to use for measurement task. Use number between 1 - 100 </td>
    </tr>

</table>

## Examples
```
  - name: Disable PCM
    dellemc.datadomain.compression:
        state: disable
        
  - name: Eanble PCM
    dellemc.datadomain.compression:
        state: enable

  - name: Eanble and initialize PCM
    dellemc.datadomain.compression:
        state: enable
        initialize: true
        
  - name: Start the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: start
        sample:
            mtrees:
                - /data/col1/mtreename01

   - name: Stop the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: stop
        sample: 
            mtrees:
                - /data/col1/mtreename01

  - name: Start the sample task for perticular mtree
    dellemc.datadomain.compression:
        state: start
        sample:
            mtrees:
                 /data/col1/mtreename01
  
  - name: Create the PCM schedule
    dellemc.datadomain.compression:
        state: create
        schedule: 
            mtrees: 
                - /data/col1/mtreename01
                - /data/col1/mtreename02
            priority: normal
            time: 10:00
            day:
                - sun
                - mon
                - tue		

  - name: Delete entities from a compression physical-capacity-measurement schedule
    dellemc.datadomain.compression:
        state: del
        schedule: 
            mtrees:
                - /data/col1/mtreename01

  - name: Destroy a schedule
    dellemc.datadomain.compression:
        state: destroy
        schedule: 
            name: test_schedule

  - name: Disable a schedule
    dellemc.datadomain.compression:
        state: disable
        schedule: 
            name: test_schedule
  
  - name: Enable a schedule
    dellemc.datadomain.compression:
        state: enable
        schedule: 
            name: test_schedule

  - name: Add a new compression physical-capacity-measurement schedule
    dellemc.datadomain.compression:
        state: modify
        schedule: 
            name: test_schedule
            priority: normal
            time: 12:00

  - name: Show Physical Capacity Reporting enable or disable status
    dellemc.datadomain.compression:
        state: status
        
  - name: Reset throttle percentage for Physical Capacity Reporting to the default value
    dellemc.datadomain.compression:
        state: reset
        throttle: '' # default value is 20 percentage


  - name: Set throttle percentage for Physical Capacity Reporting
    dellemc.datadomain.compression:
        state: set
        throttle: 50

  - name: Show throttle percentage for Physical Capacity Reporting
    dellemc.datadomain.compression:
        state: show
        throttle: ''
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

----------

# **config**
The config command manages protection system configuration settings. Command options include changing individual configuration parameters and viewing the configuration setup
## Supported Commands
  - config set admin-email $admin_email
  - config set admin-host $admin_host
  - config set location $location
  - config set mailserver $mailserver
  - config set timezone $timezone
  - config reset admin-email
  - config reset admin-mail
  - config reset location
  - config reset mailserver
  - config reset timezone

## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td><ul><li>set</li><li>reset</li></ul></td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>option</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>admin-email</li>
                <li>admin-host</li>
                <li>location</li>
                <li>mailserver</li>
                <li>timezone</li>
            </ul>
        </td>
        <td width="80%">Specify which configuration item you want to work with.</td>
    </tr>
    <tr>
        <td colspan=2>admin-email</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the admin email address here.</td>
    </tr>
    <tr>
        <td colspan=2>admin-email</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the admin email address here.</td>
    </tr>
    <tr>
        <td colspan=2>admin-host</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the admin host ip or hostname.</td>
    </tr>
    <tr>
        <td colspan=2>location</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the location of data domain like DC or rack location.</td>
    </tr>
    <tr>
        <td colspan=2>mailserver</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the mail server ip or hostname.</td>
    </tr>
    <tr>
        <td colspan=2>timezone</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Timezone names begin with Africa, America, Antarctica, Asia, Atlantic, Australia, Brazil, Canada, Chile, Europe, Indian, Mexico, Mideast, Pacific and US</td>
    </tr>
</table>

## Examples
```
- name: Reset (to default) admin-email
  dellemc.datadomain.config
    state: reset
    option: admin-email

- name: Reset (to default) admin-host
  dellemc.datadomain.config
    state: reset
    option: admin-host

- name: Reset (to default) location
  dellemc.datadomain.config
    state: reset
    option: location


- name: Reset (to default) mailserver
  dellemc.datadomain.config
    state: reset
    option: mailserver		

- name: Reset (to default) timezone
  dellemc.datadomain.config
    state: reset
    option: timezone	

- name: Reset (to default) admin-host
  dellemc.datadomain.config
    state: reset
    option: admin-host

- name: Reset (to default) location
  dellemc.datadomain.config
    state: reset
    option: location


- name: Reset (to default) mailserver
  dellemc.datadomain.config
    state: reset
    option: mailserver		

- name: Reset (to default) timezone
  dellemc.datadomain.config
    state: reset
    option: timezone		


- name: Set email address for alerts, detailed-autosupport and daily alert summary emails
  dellemc.datadomain.config
    state: set
    option: admin-email
    admin-email: abc@abc.com


- name: Set the administrative host
  dellemc.datadomain.config
    state: set
    option: admin-host
    admin-host: servername

- name: Set the administrative host
  dellemc.datadomain.config
    state: set
    option: location
    location: DCID # This could be RACK location


- name: Set the mail (SMTP) server
  dellemc.datadomain.config
    state: set
    option: mailserver
    mailserver: 10.5.23.3 # SMTP server IP/hostname


- name: Set the timezone 
  dellemc.datadomain.config
    state: set
    option: timezone
    timezone: US/Pacific 
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

----------

# **ddboost**
The ddboost command manages the integration of protection systems and disk backup devices.
Command options create and delete storage units on the storage server, and display the disk
space usage of each storage unit.
## Supported Commands
- ddboost storage-unit create $storage_unit user $user_name
- ddboost storage-unit delete $storage_unit
- ddboost storage-unit modify $storage_unit user $user_name
- ddboost storage-unit rename $storage_unit $new_storage_unit
- ddboost storage-unit undelete $storage_unit
- ddboost user assign $user_name
- ddboost user unassign $user_name
- ddboost status
- ddboost enable
- ddboost disable
## Parameters
<style >
    
    table, td, th {text-align: center; border:1px solid black;}
    li {list-style-type:square; text-align: left;}
</style>

<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>modify</li>
                <li>rename</li>
                <li>enable</li>
                <li>disable</li>
                <li>status</li>
                <li>undelete</li>
                <li>assign</li>
                <li>unassign</li>
                <li>create</li>
                <li>delete</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>storage-unit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Storage Unit name</td>
    </tr>
    <tr>
        <td colspan=2>new-storage-unit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use this option with rename. Specify new storage unit name</td>
    </tr>
    <tr>
        <td colspan=2>user-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Username to assign to ddboost protocol or storage unit</td>
    </tr>
    <tr>
        <td colspan=2>quota</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use below options to specify the quota for the storate-unit</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>quota-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Soft quota limit in format [MiB| GiB|TiB|PiB] e.g. 10 GiB</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>quota-hard-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Hard quota limit in format [MiB| GiB|TiB|PiB] e.g. 10 GiB</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>report-physical-size</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">physical report size in format n [MiB| GiB|TiB|PiB] e.g. 10 GiB
        </td>
    </tr>
    <tr>
        <td colspan=2>stream-limit</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Username to assign to ddboost protocol or storage unit</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>write-stream-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for write.</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>read-stream-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for write</td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>repl-stream-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for replication
        </td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>repl-stream-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for replication
        </td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>combined-stream-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for all read write and replication
        </td>
    </tr>
    <tr>
        <td class=elbow-placeholder></td>
        <td colspan=1>combined-stream-hard-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify soft limit for number of streams for all read write and replication
        </td>
    </tr>
</table>

## Examples

```
  - name: Enable ddboost
    dellemc.datadomain.ddboost:
        state: enable

  - name: Disable ddboost
    dellemc.datadomain.ddboost:
        state: disable

  - name: Create the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: create
        storage-unit: a001us034nve001
        user-name: a001booost
        ## Optional parameters
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 15 GiB
            report-physical-size: 10 GiB
        stream-limit:
            write-stream-soft-limit: 10 # or none - remove limit
            read-stream-soft-limit: 15 # or none - remove limit
            repl-stream-soft-limit: 13 # or none - remove limit
            combined-stream-soft-limit: 20 # or none - remove limit
            combined-stream-hard-limit: 20 # or none - remove limit		

  - name: Delete the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: delete
        storage-unit: a001us034nve001

  - name: Modify ddboost user on storage unit or Quota and/or stream-limit settings
    dellemc.datadomain.ddboost:
        state: modify
        storage-unit: a001us034nve001
        user-name: a001boost
        ## Optional parameters
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 15 GiB
            report-physical-size: 10 GiB
        stream-limit:
            write-stream-soft-limit: 10 # or none - remove limit
            read-stream-soft-limit: 15 # or none - remove limit
            repl-stream-soft-limit: 13 # or none - remove limit
            combined-stream-soft-limit: 20 # or none - remove limit
            combined-stream-hard-limit: 20 # or none - remove limit	

  - name: Rename ddboost storage unit to new name
    dellemc.datadomain.ddboost:
        state: rename
        storage-unit: a001us034nve001
        new-storage-unit: a001us034nve001-rep

  - name: Undelete the ddboost storage unit
    dellemc.datadomain.ddboost:
        state: undelete
        storage-unit: a001us034nve0

  - name: Assign the username to the ddboost protocol
    dellemc.datadomain.ddboost:
        state: assign
        user-name: a001boost

  - name: unassign the username from the ddboost protocol
    dellemc.datadomain.ddboost:
        state: unassign
        user-name: a001boost

  - name: Status of ddboost protocol
    dellemc.datadomain.ddboost:
        state: status
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **filesys**
The filesys command displays statistics, capacity, status, and use of the filesystem. Command options also clear the statistics file, and start and stop filesystem processes

## Supported Commands
-   filesys enable
-   filesys create
-   filesys clean reset $clean
-   filesys clean set $clean
-   filesys clean start
-   filesys clean stop
-   filesys encryption abort-apply-changes
-   filesys encryption apply-changes
-   filesys encryption $encryption reset
-   filesys encryption embedded-key-manager set key-rotation-policy $key_rotation_policy
-   filesys encryption key-manager set $external_key_manager
-   filesys encryption key-manager set key-rotation-policy $key_rotation_policy
-   filesys encryption algorithm set $algorithm
-   filesys encryption embedded-key-manager reset key-rotation-policy
-   filesys encryption $encryption keys create
-   filesys encryption key-manager disable
-   filesys encryption key-manager enable
-   filesys encryption disable
-   filesys encryption enable
-   filesys encryption keys delete
-   filesys encryption keys destroy
-   filesys encryption keys sync
-   filesys fastcopy source $filecopy_source destination $filecopy_destination
-   filesys status
## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disable</li>
                <li>status</li>
                <li>set</li>
                <li>reset</li>
                <li>status</li>
                <li>abort</li>
                <li>apply</li>
                <li>modify</li>
                <li>abort-apply-changes</li>
                <li>apply-changes</li>
                <li>start</li>
                <li>stop</li>
                <li>create</li>
                <li>delete</li>
                <li>destroy</li>
                <li>sync</li>
            </u>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
        <tr>
        <td colspan=2>option</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
             <ul>
                <li>encryption</li>
                <li>clean</li>
                <li>fastcopy</li>
            </ul>
        </td>
        <td width="80%">Specify which attribute of filesys you want to work on</td>
    </tr>
    <tr>
        <td colspan=2>encryption</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
             <ul>
                <li>algorithm</li>
                <li>embedded-key-manager</li>
                <li>key-manager</li>
            </ul>
        </td>
        <td width="80%">use one of the Encryption type </td>
    </tr>
    <tr>
        <td colspan=2>algorithm</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
             <ul>
                <li>aes_128_cbc</li>
                <li>aes_256_cbc</li>
                <li>aes_128_gcm</li>
                <li>aes_256_gcm</li>
            </ul>
        </td>
        <td width="80%">use one of the Encryption type </td>
    </tr>
    <tr>
        <td colspan=2>key-rotation-policy</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the key rotation policy. format - every n weeks or months or none </td>
    </tr>
    <tr>
        <td colspan=2>tier</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
             <ul>
                <li>active</li>
                <li>cloud-unit</li>
                <li>all</li>
            </ul>
        </td>
        <td width="80%">use one of the Encryption type </td>
    </tr>
    <tr>
        <td colspan=2>external-key-manager</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Following attributes of external key manager </td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>server</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Key manager server</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>port</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify port</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>fips-mode</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enabled</li>
                <li>disabled</li>
            </ul>
        </td>
        <td width="80%">fips mode enabled or disabled</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>key-class</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">specify key class</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>server-type</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>keysecure</li>
                <li>rkm</li>
            </ul>
        </td>
        <td width="80%">specify key class</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>kmip-user</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">KMIP user</td>
    </tr>
    <tr>
        <td colspan=2>key-id</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Key ID to work with. Use either Keyid or MUid</td>
    </tr>
    <tr>
        <td colspan=2>muid</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">MUID to work with. Use either Keyid or MUid</td>
    </tr>
    <tr>
        <td colspan=2>ext-key-manager-state</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">ext key manager state - deactivated</td>
    </tr>
    <tr>
        <td colspan=2>fastcopy-source</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Fastcopy Source Mtree path</td>
    </tr>
    <tr>
        <td colspan=2>fastcopy-destination</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Fastcopy destination Mtree path</td>
    </tr>
    <tr>
        <td colspan=2>clean</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Filesystem cleaning schedule and throttle</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>schedule</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Schedule cleaning never or daily (time) or (day(s)) (time) or biweekly (day) (time) or monthly (day(s)) (time)</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>throttle</td>
        <td width="20%">int</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify the CPU throttle percentage in number like 40 </td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>all</td>
        <td width="20%">int</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use only when state is reset. This will reset both Schedule and Throttle to default values</td>
    </tr>
</table>
## Examples

```
  - name:  Reset (to default) the schedule/Throttle/all (both)
    dellemc.datadomain.filesys:
        state: reset
        operation: clean
        clean:
            schedule: "" # use throttle or all

  - name:  Set the Schedule
    dellemc.datadomain.filesys:
        state: set
        operation: clean
        clean:
            schedule: daily 11:00

  - name:  Set (to default) the Throttle
    dellemc.datadomain.filesys:
        state: set
        operation: clean
        clean:
            throttle: 60

  - name:  Start the cleaning
    dellemc.datadomain.filesys:
        state: start
        operation: clean

  - name:  Check clean status
    dellemc.datadomain.filesys:
        state: status
        operation: clean

  - name:  Stop the cleaning operation
    dellemc.datadomain.filesys:
        state: stop
        operation: clean

  - name:  Creates a filesystem with the active tier storage
    dellemc.datadomain.filesys:
        state: create
 
  - name:  Enable file system operations
    dellemc.datadomain.filesys:
        state: enable
        
  - name:   Abort previously issued apply-changes request
    dellemc.datadomain.filesys:
        state: abort-apply-changes
        operation: encryption
                                      
                                       
  - name:  Reset the encryption algorithm to default (aes_256_cbc)
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: algorithm

    - name: Set the encryption algorithm [aes_128_cbc | aes_256_cbc | aes_128_gcm | aes_256_gcm]
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: algorithm
        algorithm: aes_128_gcm
                                                    

  - name:  Apply current encryption configuration to filesystem
    dellemc.datadomain.filesys:
        state: apply-changes
        operation: encryption

   - name:  Disable encryption
    dellemc.datadomain.filesys:
        state: disable
        operation: encryption
        tier: active  #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Create a new key
    dellemc.datadomain.filesys:
        state: create
        operation: encryption
        encryption: embedded-key-manager

  - name:  Reset key-rotation-policy of embedded-key-manager.
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: embedded-key-manager
                                      
  - name:  Setup key-rotation-policy of embedded-key-manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: embedded-key-manager
        key-rotation-policy: 10
                                       

  - name:  Enable encryption
    dellemc.datadomain.filesys:
        state: enable
        operation: encryption
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Disable RKM/KeySecure
    dellemc.datadomain.filesys:
        state: disable
        operation: encryption
        encryption: key-manager

  - name:  Enable RKM/KeySecure
    dellemc.datadomain.filesys:
        state: enable
        operation: encryption
        encryption: key-manager
                                       
  - name:  Create a new external key manager key
    dellemc.datadomain.filesys:
        state: create
        operation: encryption
        encryption: key-manager
                                       

  - name:  Reset key manager attributes
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: key-manager
                                       
  - name:  Reset key-rotation-policy of external key manager.
    dellemc.datadomain.filesys:
        state: reset
        operation: encryption
        encryption: key-manager
        key-rotation-policy: ""
                                       

  - name:  Set key-rotation-policy of external key manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: key-manager
        key-rotation-policy: every 1 month # format - every <n> {weeks | months} | none
                                       

  - name:  Mark the key as deleted
    dellemc.datadomain.filesys:
        state: delete
        operation: encryption
        key-id: 1 # use one of <key-id> | muid <key-muid>
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]

  - name:  Mark the key as destroyed
    dellemc.datadomain.filesys:
        state: delete
        operation: encryption
        key-id: 1 # use one of <key-id> | muid <key-muid>
        tier: active # #optional parameter [active | cloud-unit {<unit-name> | all}]
                
                                       
  - name: Sync the keys with the Key Manager
    dellemc.datadomain.filesys:
        state: sync
        operation: encryption
 
  - name: Create External Key Manager
    dellemc.datadomain.filesys:
        state: set
        operation: encryption
        encryption: key-manager
        external-key-manager:
            server: 10.15.150.19
            port: 2125
            fips-mode: enabled
            server-type: keysecure
            key-class: classic
            kmip-user: sudarshan

```

## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **mtree**
The mtree command enables operations on a single “managed tree” (MTree) of a filesystem. An MTree is a logical partition of the namespace in the file system that can group together a set of files for management purposes; for example, snapshot schedules, replication, or retention locking.
## Supported Commands
-   mtree alias create $alias_name mtree
-   mtree create 
-   mtree alias delete 
-   mtree delete 
-   mtree rename 
-   mtree modify 
-   mtree option set anchoring-algorithm 
-   mtree option set app-optimized-compression 
-   mtree option set randomio 
-   mtree option reset anchoring-algorithm mtree 
-   mtree option reset app-optimized-compression mtree 
-   mtree option reset randomio mtree 
-   mtree retention-lock enable mode
-   mtree retention-lock disable mtree 
-   mtree retention-lock set 
-   mtree retention-lock reset 
-   mtree undelete 
## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>create</li>
                <li>delete</li>
                <li>rename</li>
                <li>enable</li>
                <li>disable</li>
                <li>set</li>
                <li>reset</li>
                <li>list</li>
                <li>undelete</li>
            </ul>
      </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>mtree-path</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Mtree Path</td>
    </tr>
    <tr>
        <td colspan=2>new-mtree-path</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">New Mtree Path when you want to rename the mtree</td>
    </tr>
    <tr>
        <td colspan=2>alias-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Mtree Alias name</td>
    </tr>
    <tr>
        <td colspan=2>tenant-unit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Tenant unit name</td>
    </tr>
    <tr>
        <td colspan=2>anchoring-algorithm</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>variable</li>
                <li>fixed</li>
                <li>""</li>
            </ul>
        </td>
        <td width="80%">Algorithm type</td>
    </tr>
    <tr>
        <td colspan=2>app-optimized-compression</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>none</li>
                <li>global</li>
                <li>oracle1</li>
            </ul>
        </td>
        <td width="80%">app optimized compression</td>
    </tr>
    <tr>
        <td colspan=2>randomio</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disable</li>
            </ul>
        </td>
        <td width="80%">random io settings</td>
    </tr>
    <tr>
        <td colspan=2>retention-lock</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>compliance</li>
                <li>governance</li>
                <li>""</li>
            </ul>
        </td>
        <td width="80%">random io settings</td>
    </tr>
    <tr>
        <td colspan=2>quota</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">quota settings for mtree</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>quota-soft-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Soft limit format n MiB | GiB | TiB| PiB</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>quota-hard-limit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">hard limit format n MiB | GiB | TiB| PiB</td>
    </tr>
    <tr>
        <td colspan=2>retention</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Retention lock settings for retention period</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-retention-period</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Minimum retention periods format 720Minutes | days</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>max-retention-period</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Max retention period format 720Minutes | days</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>automatic-retention-period</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Automatic retention period format 720Minutes | days</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>automatic-lock-delay</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">automatic retention lock delay format 120Minutes</td>
    </tr>
</table>
## Examples

```
  - name: Get the list of MTrees
    dellemc.datadomain.mtree:
        state: list
        
  - name: Create a MTree
    dellemc.datadomain.mtree:
        state: create
        mtree-path: /data/col1/a001us043nve001
        quota:
            quota-soft-limit: 10 GiB
            quota-hard-limit: 12 GiB

  - name: Delete a MTree
    dellemc.datadomain.mtree:
        state: delete
        mtree-path: /data/col1/a001us043nve001


  - name: Rename a MTree
    dellemc.datadomain.mtree:
        state: rename
        mtree-path: /data/col1/a001us043nve001
        new-mtree-path: /data/col1/a001us043nve002

  - name:  Set anchoring-algorithm
    dellemc.datadomain.mtree:
        state: set
        mtree-path: /data/col1/a001us043nve001
        anchoring-algorithm: variable

  - name:   Disables retention-lock for specified MTree.
    dellemc.datadomain.mtree:
        state: disable
        mtree-path: /data/col1/a001us043nve001
        retention-lock: ""

  - name:  Enables retention-lock for specified MTree.
    dellemc.datadomain.mtree:
        state: enable
        mtree-path: /data/col1/a001us043nve001
        retention-lock: compliace

  - name:  Reset retention periods to default for specified MTree.
    dellemc.datadomain.mtree:
        state: reset
        mtree-path: /data/col1/a001us043nve001
        retention:
            min-retention-period: ""

  - name:  Set retention periods for specified MTree.
    dellemc.datadomain.mtree:
        state: set
        mtree-path: /data/col1/a001us043nve001
        retention:
            min-retention-period: 720Minuets 

  - name: Undelete a MTree
    dellemc.datadomain.mtree:
        state: undelete
        mtree-path: /data/col1/a001us043nve001  - name: Create a MTree
```

## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **net**
The net command manages the use of all IP network features and displays network information and status.
## Supported Commands
-   net aggregate add
-   net aggregate del
-   net aggregate modify
-   net config
-   net create interface
-   net create virtual veth
-   net destroy
-   net enable 
-   net failover add 
-   net failover del 
-   net failover modify 
-   net hosts add
-   net hosts del
-   net hosts reset
-   net lookup
-   net ping 
-   net reset domainname
-   net reset searchdomains
-   net reset dns
-   net reset hostname
-   net route add net 
-   net route add host 
-   net route del net 
-   net route del host 
-   net set domainname 
-   net set searchdomains 
-   net set dns
-   net set hostname 

## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            </ul>
                <li>config</li>
                <li>create</li>
                <li>disable</li>
                <li>enable</li>
                <li>add</li>
                <li>del</li>
                <li>reset</li>
                <li>set</li>
                <li>destroy</li>
                <li>test</li>
                <li>modify</li>
                <li>show</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>ifname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">interface name</td>
    </tr>
    <tr>
        <td colspan=2>ifname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">interface name</td>
    </tr>
    <tr>
        <td colspan=2>ipaddr</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">IP address</td>
    </tr>
    <tr>
        <td colspan=2>netmask</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Subnet mask </td>
    </tr>
    <tr>
        <td colspan=2>gateway</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Gateway for the network/Ip</td>
    </tr>
    <tr>
        <td colspan=2>mtu</td>
        <td width="20%">int</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Maximum Transmission unit</td>
    </tr>
    <tr>
        <td colspan=2>vethid</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">virtual ethernet number</td>
    </tr>
    <tr>
        <td colspan=2>physical-ifname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Physical interface names like eth4a</td>
    </tr>
    <tr>
        <td colspan=2>virtual-ifname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">virtual interface name like veth4</td>
    </tr>
    <tr>
        <td colspan=2>vlan</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">VLAN ID</td>
    </tr>
    <tr>
        <td colspan=2>network</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Network IP </td>
    </tr>
    <tr>
        <td colspan=2>option</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>hosts</li>
                <li>route</li>
                <li>dns</li>
                <li>hostname</li>
                <li>domainname</li>
                <li>searchdomains</li>
                <li>ping</li>
                <li>lookup</li>
                <li>aggregate</li>
                <li>failover</li>
            </ul>
        </td>
        <td width="80%">Choose on which network attribute you want to run command</td>
    </tr>
    <tr>
        <td colspan=2>host-list</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use when you want to add hosts entry on Data domain Host list in the format IP FQDN hostname</td>
    </tr>
    <tr>
        <td colspan=2>count</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use when you want to perform ping test on IP. Specify how many times you want to ping the IP</td>
    </tr>
    <tr>
        <td colspan=2>domainname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Domain name for the data domain</td>
    </tr>
    <tr>
        <td colspan=2>searchdomains</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">DSearch domain names</td>
    </tr>
    <tr>
        <td colspan=2>hostname</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Hostname for the data domain</td>
    </tr>
    <tr>
        <td colspan=2>dns</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">DNS IPs </td>
    </tr>
    <tr>
        <td colspan=2>aggregate</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Select aggregate attributes</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>mode</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>roundrobin</li>
                <li>balanced</li>
                <li>lacp</li>
            </ul>
        </td>
        <td width="80%">Aggregate mode</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>hash</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>xor-L2</li>
                <li>xor-L3L4</li>
                <li>xor-L2L3</li>
            </ul>
        </td>
        <td width="80%">Hash mode</td>
    </tr>
    <tr>
        <td colspan=2>failover</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">select failover attribute</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>primary</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Select primary physical interface</td>
    </tr>
    <tr>

</table>
## Examples

```
  - name:  Add slave interfaces to an aggregate interface
    dellemc.datadomain.net:
        state: add
        option: aggregate
        virtual-ifname: veth0
        physical-ifname: eth5a eth4a
        aggregate:
            mode: lacp
            hash: xor-L3L4

  - name:  Show Network settings
    dellemc.datadomain.net:
        state: show
        
  - name:  Delete network interfaces from an aggregate interface
    dellemc.datadomain.net:
        state: del
        option: aggregate
        virtual-ifname: veth0
        physical-ifname: eth5a
   
  - name:  Modify the configuration of an aggregate interface
    dellemc.datadomain.net:
        state: modify
        option: aggregate
        virtual-ifname: veth0
        aggregate:
            hash: xor-L2L3

  - name:  Configure an Ethernet interface.
    dellemc.datadomain.net:
        state: config
        ifname: veth0.2345
        ipaddr: 100.64.65.149
        netmask: 255.255.255.240
        mtu: 9600 # Optional Parameter

  
  - name: Create a VLAN interface
    dellemc.datadomain.net:
        state: create
        ifname: veth0
        vlan: 2639

  - name: Create a virtual interface
    dellemc.datadomain.net:
        state: create
        vethid: '01'
 
  - name: Destroy a VLAN interface
    dellemc.datadomain.net:
        state: destroy
        ifname: veth01.2639
                                       
  - name: Enable an Ethernet interface
    dellemc.datadomain.net:
        state: enable
        ifname: veth01.2639

  - name:  Add network interfaces to a failover interface
    dellemc.datadomain.net:
        state: add
        option: failover
        virtual-ifname: veth0
        ifname: eth1a eth2b
        failover:
            primary: eth1a

                                    
  - name: Delete network interfaces from a failover interface
    dellemc.datadomain.net:
        state: del
        option: failover
        virtual-ifname: veth0
        ifname: eth1a
                   
  - name: Modify the primary network interface for a failover interface
    dellemc.datadomain.net:
        state: modify
        option: failover
        virtual-ifname: veth0
        failover:
            primary: eth2a                                      
   - name: Add a host list entry
    dellemc.datadomain.net:
        state: add
        option: hosts
        host-list: 100.64.65.100    a001us034nve001.usp01.xstream360.cloud  a001us034nve001

  - name: Delete a host list entry
    dellemc.datadomain.net:
        state: del
        option: hosts
        ipaddr: 100.64.65.100

  - name: Clear the hosts list
    dellemc.datadomain.net:
        state: reset
        option: hosts

  - name: Lookup DNS entries
    dellemc.datadomain.net:
        state: test
        option: lookup
        ipaddr: 100.64.65.150

  - name: Ping a host
    dellemc.datadomain.net:
        state: test
        option: ping
        ipaddr: 100.64.65.150
        count: 3

  - name: Reset (to default) the domainname
    dellemc.datadomain.net:
        state: reset
        option: domainname

  - name:  Reset (to default) the searchdomains
    dellemc.datadomain.net:
        state: reset
        option: searchdomains
  
  - name: Reset (to default) the DNS list
    dellemc.datadomain.net:
        state: reset
        option: dns 
        
  - name: Reset (to default) the hostname
    dellemc.datadomain.net:
        state: reset
        option: hostname

  - name: Add a network route rule
    dellemc.datadomain.net:
        state: add
        option: route
        network: 100.64.65.144
        gateway: 100.68.65.97
        netmask: 255.255.255.240
        ifname: eth0.2639	

  - name:  Add a host route rule
    dellemc.datadomain.net:
        state: add
        option: route
        ipaddr: 100.64.65.150
        gateway: 100.68.65.97
        ifname: eth0.2639
  

  - name: Remove a host routing rule
    dellemc.datadomain.net:
        state: del
        option: route
        ipaddr: 100.64.65.150
        gateway: 100.68.65.97
        ifname: eth0.2639

  - name: Remove a network routing rule
    dellemc.datadomain.net:
        state: del
        option: route
        network: 100.64.65.144
        netmask: 255.255.255.240
        gateway: 100.68.65.97
        ifname: eth0.2639

  - name: Set the domainname
    dellemc.datadomain.net:
        state: set
        option: domainname
        domainname: abc.com

  - name: Set the searchdomains
    dellemc.datadomain.net:
        state: set
        option: searchdomains
        searchdomains: abc.com
                               
  - name: Set the dns
    dellemc.datadomain.net:
        state: set
        option: dns
        dns: 10.15.10.2 10.15.2.10
  
   - name: Set the hostname
     dellemc.datadomain.net:
        state: set
        option: hostname
        hostname: a001us033dd1003
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **nfs**
The nfs command enables you to add NFS clients and manage access to a protection system. It also enables you to display status information, such as verifying that the NFS system is active, and the time required for specific NFS operations.

## Supported Commands
-   nfs export add $export_name clients $client_list
-   nfs export del $export_name clients $client_list
-   nfs disable
-   nfs enable
-   nfs export create $export_name path $path clients $client_list
-   nfs export destroy $export_name
-   nfs export modify $export_name clients $client-list options $export_options
-   nfs export rename $export_name $new_export_name
-   nfs reset clients
-   nfs restart
-   nfs status

## Parameters
<table>
    <tr>
        <th colspan=1>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=1>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>add</li>
                <li>del</li>
                <li>create</li>
                <li>destroy</li>
                <li>enable</li>
                <li>disable</li>
                <li>modify</li>
                <li>rename</li>
                <li>reset</li>
                <li>set</li>
                <li>restart</li>
                <li>status</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=1>path</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">mtree or directory path on the data domain</td>
    </tr>
    <tr>
        <td colspan=1>client-list</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">list of clients to allow access to export</td>
    </tr>
    <tr>
        <td colspan=1>version</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">NFS Version</td>
    </tr>
    <tr>
        <td colspan=1>export-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Export name</td>
    </tr>
    <tr>
        <td colspan=1>new-export-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">new export name</td>
    </tr>
    <tr>
        <td colspan=1>export-options</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">export options like 'rw,no_root_squash,no_all_squash,secure'</td>
    </tr>
</table>

## Examples

```
  - name: Disable NFS clients from connecting
    dellemc.datadomain.nfs:
        state: disable
        
  - name: Enable NFS clients to connect
    dellemc.datadomain.nfs:
        state: enable

  - name: Add a client to an export
    dellemc.datadomain.nfs:
        state: add
        export-name: backupserver01
        client-list: 10.0.0.6 10.0.0.7
 
  - name: Create an export, optionally add clients
    dellemc.datadomain.nfs:
        state: create
        export-name: backupserver01
        path: /data/col1/backupserver01
        client-list: 10.0.0.3 10.0.0.4
        export-options: 'rw,no_root_squash,no_all_squash,secure'
                                       

  - name: remove a client from an export
    dellemc.datadomain.nfs:
        state: del
        export-name: backupserver01
        client-list: 10.0.0.6 10.0.0.7								   
  
  - name: Destroy and export
    dellemc.datadomain.nfs:
        state: destroy
        export-name: backupserver01

  - name: Modify an export, clients and/or export options
    dellemc.datadomain.nfs:
        state: create
        export-name: backupserver01
        path: /data/col1/backupserver01
        client-list: 10.0.0.3 10.0.0.4
        export-options: 'rw,no_root_squash,no_all_squash,secure'

  - name: Rename an export
    dellemc.datadomain.nfs:
        state: rename
        export-name: backupserver01
        new-export-name: backupserver02
 
 
  - name: Reset (to default) the NFS client list
    dellemc.datadomain.nfs:
        state: reset

  - name: Restart NFS servers
    dellemc.datadomain.nfs:
        state: restart
        version: 4 # OPtiona field. Also you can type All to 

  
  - name: Restart NFS servers
    dellemc.datadomain.nfs:
        state: status
```

## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **ntp**
The ntp command synchronizes a protection system with an NTP time server, manages the NTP
service, or turns off the local NTP server.

## Supported Commands
-   ntp add timeserver $timeserver
-   ntp del timeserver $timeserver
-   ntp reset timeserver
-   ntp enable
-   ntp disable
-   ntp reset
-   ntp sync
-   ntp status

## Parameters

<table>
    <tr>
        <th colspan=1>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=1>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>add</li>
                <li>del</li>
                <li>enable</li>
                <li>disable</li>
                <li>reset</li>
                <li>sync</li>
                <li>status</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=1>timeserver</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Time server IP or hostname</td>
    </tr>
</table>

## Examples

```
  - name: Add one or more remote time servers
    dellemc.datadomain.ntp:
        state: add
        timeserver: 10.5.0.2 10.5.0.3

  - name: Delete one or more remote time servers
    dellemc.datadomain.ntp:
        state: del
        timeserver: 10.5.0.3

  - name: Disable the NTP local server
    dellemc.datadomain.ntp:
        state: disable

  - name: enable the NTP local server
    dellemc.datadomain.ntp:
        state: enable

  - name: Reset (to default) the NTP server configuration
    dellemc.datadomain.ntp:
        state: reset

  - name: Reset (to default) remote time servers
    dellemc.datadomain.ntp:
        state: reset
        timeserver: ''

  - name: Show the local NTP server status
    dellemc.datadomain.ntp:
        state: status

  - name: Sync with a configured NTP server
    dellemc.datadomain.ntp:
        state: sync
```
## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **replication**
DD Replicator lets you replicate data (copy and synchronize) between two protection systems: a source and a destination. Source and destination configurations, or pairs, are also known as “contexts.”
## Supported Commands

-   replication add 
-   replication break 
-   replication disable 
-   replication enable 
-   replication initialize 
-   replication modify 
-   replication option reset
-   replication option set
-   replication resync
-   replication sync
-   replication status

## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disable</li>
                <li>add</li>
                <li>break</li>
                <li>modify</li>
                <li>resync</li>
                <li>sync</li>
                <li>initialize</li>
                <li>status</li>
                <li>show</li>
                <li>set</li>
                <li>reset</li>
                <li>recover</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>source</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Replication source Mtree in format mtree://ddhostname/mtree path</td>
    </tr>
    <tr>
        <td colspan=2>destination</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Replication destination Mtree in format mtree://ddhostname/mtree path</td>
    </tr>
    <tr>
        <td colspan=2>low-bw-optim</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
            </ul>
        </td>
        <td width="80%">Low bandwidth optimization</td>
    </tr>
    <tr>
        <td colspan=2>encryption</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Encryption</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>state</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
            </ul>
        </td>
        <td width="80%">Use this parameter to enable or disable encryption</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>authentication-mode</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>one-way</li>
                <li>two-way</li>
                <li>anonymous</li>
            </ul>
        </td>
        <td width="80%">auth mode only when Encryption is enabled</td>
    </tr>
    <tr>
        <td colspan=2>propagate-retention-lock</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enabled</li>
                <li>disabled</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
      <tr>
        <td colspan=2>ipversion</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>ipv4</li>
                <li>ipv6</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>max-repl-streams</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">maximum replication streams</td>
    </tr>
        <tr>
        <td colspan=2>destination-tenant-unit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Destination Tenant Unit name</td>
    </tr>
    <tr>
        <td colspan=2>option</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Replication option settings</td>
    </tr>
    <tr>
        <td colspan=2>option</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Replication option settings</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>bandwidth</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Set the network bandwidth (Bps) for thedes restorer</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>delay</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Set the network delay (ms) for the restorer</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>listen-port</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Set the listen port for the restorer</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>default-sync-alert-threshold</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Set the sync-time (in hrs) when alert is raised</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>enforce-fips-compliance:</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enabled</li>
                <li>disabled</li>
            </ul>
        </td>
        <td width="80%">SEnforce FIPS compliance mode</td>
    </tr>
    <tr>
        <td colspan=2>repl-port</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify port to be used for replication</td>
    </tr>
    <tr>
        <td colspan=2>connection-host</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Specify IP of the remote data domain for replication</td>
    </tr>
    <tr>
        <td colspan=2>source-host</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use when you modify the source host of replication context</td>
    </tr>
    <tr>
        <td colspan=2>destination-host</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Use when you modify the destination host of replication context</td>
    </tr>
</table>
## Examples

```
  - name: Add a replication pair
    dellemc.datadomain.replication:
        state: add
        source: mtree://source.datadomain.name/data/col1/source
        destination: mtree://destination.datadomain.name/data/col1/destination
        #optional parameters
        low-bw-optim: enabled
        encryption: 
            state: enabled
            authentication-mode: one-way # This option only used when encryption is enabled.
        propagate-retention-lock: enabled
        ipversion: ipv4
        max-repl-streams: 5

  - name: break  and remove replication to the specified destination
    dellemc.datadomain.replication:
        state: break
        destination: mtree://destination.datadomain.name/data/col1/destination

  - name: Disable replication
    dellemc.datadomain.replication:
        state: disable
        destination: mtree://destination.datadomain.name/data/col1/destination
                                 
  - name: Enable replication
    dellemc.datadomain.replication:
        state: enable
        destination: mtree://destination.datadomain.name/data/col1/destination

  - name: Initialize replication on the source
    dellemc.datadomain.replication:
        state: initialize
        destination: mtree://destination.datadomain.name/data/col1/destination
                         
  - name: Reconfigure replication context for new source host
    dellemc.datadomain.replication:
        state: modify
        destination: mtree://destination.datadomain.name/data/col1/destination
        connection-host: 10.0.0.1

  - name: Reconfigure replication context for low bandwidth optimization
    dellemc.datadomain.replication:
        state: modify
        destination: mtree://destination.datadomain.name/data/col1/destination
        low-bw-optim: enabled

  - name: Reconfigure replication context for low bandwidth optimization
    dellemc.datadomain.replication:
        state: set
        option:
            bandwidth: 50 #Set the network bandwidth (Bps) for the des restorer
            delay: 100 #Set the network delay (ms) for the restorer

  - name: Resynchronize replication between the source and destination
    dellemc.datadomain.replication:
        state: resync
        destination: mtree://destination.datadomain.name/data/col1/destination

```

## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>

# **users**
## Supported Commands
-   Create User
-   Delete User
-   Change user role
-   User enable/disable
-   set/reset user aging option
-   set/reset default aging and password strength option
## Parameters
<table>
    <tr>
        <th colspan=2>Parameter</th>
        <th width="20%">Type</th>
        <th>Required</th>
        <th>Default</th>
        <th width="25%">Choices</th>
        <th width="70%">Description</th>
    </tr>
    <tr>
        <td colspan=2>state</td>
        <td width="20%">str</td>
        <td>Yes</td>
        <td></td>
        <td>
            <ul>
                <li>add</li>
                <li>del</li>
                <li>change</li>
                <li>enable</li>
                <li>disable</li>
                <li>set</li>
                <li>reset</li>
                <li>show</li>
            </ul>
        </td>
        <td width="80%">Select the action from the choices</td>
    </tr>
    <tr>
        <td colspan=2>user-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Type the User name</td>
    </tr>
    <tr>
        <td colspan=2>role-name</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>admin</li>
                <li>limited-admin</li>
                <li>user</li>
                <li>backup-operator</li>
                <li>none</li>
            </ul>
        </td>
        <td width="80%">Select the user role from above options</td>
    </tr>
    <tr>
        <td colspan=2>user-password</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Type the User Password</td>
    </tr>
    <tr>
        <td colspan=2>dd-password</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Data domain admin or Sysadmin User password. This is only required when you want to create new user or change existing user password. </td>
    </tr>
    <tr>
        <td colspan=2>new-password</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">New user password</td>
    </tr>
    <tr>
        <td colspan=2>aging</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">User password aging options.</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-days-between-change</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">minimum days between password change</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>disable-days-after-expire</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Days after which user will be expired</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>max-days-between-change</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Max days between password change</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>max-days-between-change</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Max days between password change</td>
    </tr>
    <tr>
        <td colspan=2>strength</td>
        <td width="20%">dict</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Password strength options.</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-length</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">minimum password strength</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-character-classes</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">minimum character classes</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-one-lowercase</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
				<li>""</li>
            </ul>
        </td>
        <td width="80%">minimum lowercase characters</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-one-uppercase</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
				<li>""</li>
            </ul>
        </td>
        <td width="80%">minimum uppercase characters</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-one-digit</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
				<li>""</li>
            </ul>
        </td>
        <td width="80%">minimum digit characters</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>min-one-special</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
				<li>""</li>
            </ul>
        </td>
        <td width="80%">minimum special characters</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>max-three-repeat</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td>
            <ul>
                <li>enable</li>
                <li>disabled</li>
				<li>""</li>
            </ul>
        </td>
        <td width="80%">Max last three password repeat</td>
    </tr>
    <tr>
        <td class="elbow-placeholder"></td>
        <td colspan=1>passwords-remembered</td>
        <td width="20%">str</td>
        <td>No</td>
        <td></td>
        <td></td>
        <td width="80%">Reset the number of remembered passwords to 1</td>
    </tr>
</table>

## Examples

```
  - name:  Add a new user
    dellemc.datadomain.users:
        state: add
        user-name: boostuser04
        role-name: admin
        user-password: password01
        dd-password: password02

  - name:  Change the password for a user
    dellemc.datadomain.users:
        state: change
        user-name: boostuser04
        new-password: password04
        user-password: password01
        dd-password: password02


  - name: Change the role of a user
    dellemc.datadomain.users:
        state: change
        user-name: boostuser04
        role-name: user

  - name:  Remove a user
    dellemc.datadomain.users:
        state: del
        user-name: boostuser04


  - name:  Disable the user's account
    dellemc.datadomain.users:
        state: disable
        user-name: boostuser04

  - name:  Enable the user's account
    dellemc.datadomain.users:
        state: enable
        user-name: boostuser04

  - name: Reset the default password aging policy
    dellemc.datadomain.users:
        state: reset
        aging:
            min-days-between-change: ""
            max-days-between-change: ""
            warn-days-before-expire: ""
            disable-days-after-expire: ""

  - name: Set the default password aging policy
    dellemc.datadomain.users:
        state: set
        aging:
            min-days-between-change: 999
            max-days-between-change: 9999
            warn-days-before-expire: 9998
            disable-days-after-expire: 10000}


  - name:  Reset the password aging policy for a user
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        aging:
            min-days-between-change: ""
            max-days-between-change: ""
            warn-days-before-expire: ""
            disable-days-after-expire: ""

  - name:  Set the password aging policy for a user
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        aging:
            min-days-between-change: 999
            max-days-between-change: 9999
            warn-days-before-expire: 9998
            disable-days-after-expire: 10000


  - name:  Reset the password strength policy to defaults
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        strength:
            min-length: ""
            min-character-classes: ""
            min-one-lowercase: ""
            min-one-uppercase: ""
            min-one-digit: ""
            min-one-special: ""
            max-three-repeat: ""
            passwords-remembered: ""

  - name:  Set the password strength policy
    dellemc.datadomain.users:
        state: reset
        user-name: boostuser04
        strength:
            min-length: 10
            min-character-classes: 2
            min-one-lowercase: enabled
            min-one-uppercase: disabled
            min-one-digit: enabled
            min-one-special: enabled
            max-three-repeat: enabled
            passwords-remembered: 2
```

## Authors
Sudarshan Kshirsagar (@kshirs1)

<div style="text-align: right"><a href="#contents">Back to Contents</a></div>