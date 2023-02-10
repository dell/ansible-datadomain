# Copyright ©️ 2022 Dell Inc. or its subsidiaries.
def replication():
    conditions = dict(
        replication_add=dict(query=dict(state='add'), req_key=['source', 'destination'],
                             opt_key=['low-bw-optim', 'encryption', 'propagate-retention-lock', 'ipversion', 'max-repl-streams', 'destination-tenant-unit'], will_change=True, header=None),
        replication_break=dict(query=dict(state='break'), req_key=['destination'], will_change=True, header=None),
        replication_disable=dict(query=dict(state='disable'), req_key=['destination'], will_change=True, header=None),
        replication_enable=dict(query=dict(state='enable'), req_key=['destination'], will_change=True, header=None),
        replication_initialize=dict(query=dict(state='initialize'), req_key=['destination'],
                                    will_change=True, header=None),
        replication_modify=dict(query=dict(state='modify'), req_key=['destination'], 
                    opt_key=['repl-port', 'low-bw-optim', 'encryption', 'max-repl-streams', 'destination-tenant-unit', 'crepl-gc-bw-optim', 'source-host', 'destination-host'], 
                                       will_change=True, header=None),
        replication_option_set=dict(query=dict(state='set'), req_key=['option'], 
                    opt_key=[], will_change=True, header=None),
        replication_option_reset=dict(query=dict(state='reset'), req_key=['option'], 
                    opt_key=[], will_change=True, header=None),
        replication_resync=dict(query=dict(state='resync'), req_key=['destination'], will_change=True, header=None),
        replication_sync=dict(query=dict(state='sync'), req_key=['destination'], will_change=True, header=None),
        replication_recover=dict(query=dict(state='recover'), req_key=['destination'], will_change=True, header=None),
        replication_status=dict(query=dict(state='status'), req_key=[], will_change=True, header=None),
        replication_show_option=dict(query=dict(state='show'), req_key=['option'], will_change=False, header=None),
        replication_show_config=dict(query=dict(state='show'), req_key=[], will_change=False, opt_key=['destination'],
                                     header=["ctx", "source", "destination", "connection_host", "connection_port", "low-bw-optim", "repl-gc-bw-optim", "encryption", "enabled", "max-repl-streams"]),
        
    )

    supported_commands = dict(replication_add='["replication add source $source destination $destination"]',
                              replication_break='["replication break $destination"]',
                              replication_disable='["replication disable $destination"]',
                              replication_enable='["replication enable $destination"]',
                              replication_initialize='["replication initialize $destination"]',
                              replication_modify='["replication modify $destination"]',
                              replication_option_set='["replication option set $option"]',
                              replication_option_reset='["replication option reset $option"]',
                              replication_option_modify='["replication modify $destination $replication_options"]',
                              replication_resync='["replication resync $destination"]',
                              replication_sync='["replication sync $destination"]',
                              replication_recover='["replication recover $destination"]',
                              replication_status='["replication status"]',
                              replication_show_config='["replication show config"]',
                              replication_show_option='["replication option show"]'

                              )
    return conditions, supported_commands


def ntp():
    conditions = dict(
        ntp_timeserver_add=dict(query=dict(state='add'), req_key=['timeserver'], will_change=True, header=None),
        ntp_timeserver_del=dict(query=dict(state='del'), req_key=['timeserver'], will_change=True, header=None),
        ntp_timeserver_reset=dict(query=dict(state='reset'), req_key=['timeserver'], will_change=True, header=None),
        ntp_enable=dict(query=dict(state='enable'), req_key=[], will_change=True, header=None),
        ntp_disable=dict(query=dict(state='disable'), req_key=[], will_change=True, header=None),
        ntp_reset=dict(query=dict(state='reset'), req_key=[], will_change=True, header=None),
        ntp_sync=dict(query=dict(state='sync'), req_key=[], will_change=True, header=None),
        ntp_status=dict(query=dict(state='status'), req_key=[], will_change=True, header=None),
        ntp_show=dict(query=dict(state='show'), req_key=[], will_change=False, header=None)

    )

    supported_commands = dict(ntp_timeserver_add='["ntp add timeserver $timeserver"]',
                              ntp_timeserver_del='["ntp del timeserver $timeserver"]',
                              ntp_timeserver_reset='["ntp reset timeserver"]',
                              ntp_enable='["ntp enable"]',
                              ntp_disable='["ntp disable"]',
                              ntp_reset='["ntp reset"]',
                              ntp_sync='["ntp sync"]',
                              ntp_status='["ntp status"]',
                              ntp_show='["ntp show config"]',

                              )
    return conditions, supported_commands


def nfs():
    conditions = dict(
        nfs_export_add=dict(query=dict(state='add'), req_key=['export-name', 'clients'], will_change=True, header=None),
        nfs_export_del=dict(query=dict(state='del'), req_key=['export-name', 'clients'], will_change=True, header=None),
        nfs_disable=dict(query=dict(state='disable'), req_key=[], opt_key=['version'], will_change=True, header=None),
        nfs_enable=dict(query=dict(state='enable'), req_key=[], opt_key=['version'], will_change=True, header=None),
        nfs_export_create=dict(query=dict(state='create'), req_key=['export-name', 'path'],
                               opt_key=['clients', 'export-options'], will_change=True, header=None),
        nfs_export_destroy=dict(query=dict(state='destroy'), req_key=['export-name'], will_change=True, header=None),
        nfs_export_modify=dict(query=dict(state='modify'),
                               req_key=['export-name', 'clients', 'path', 'export-options'],
                               will_change=True, header=None),
        nfs_export_rename=dict(query=dict(state='rename'), req_key=['export-name', 'new-export-name'],
                               will_change=True, header=None),
        nfs_client_reset=dict(query=dict(state='reset'), req_key=[], will_change=True, header=None),
        nfs_restart=dict(query=dict(state='restart'), req_key=[], opt_key=['version'], will_change=True, header=None),
        nfs_status=dict(query=dict(state='status'), req_key=[], will_change=True, header=None),

    )

    supported_commands = dict(nfs_export_add='["nfs export add $export_name clients $cliens"]',
                              nfs_export_del='["nfs export del $export_name clients $clients"]',
                              nfs_disable='["nfs disable"]',
                              nfs_enable='["nfs enable"]',
                              nfs_export_create='["nfs export create $export_name path $path"]',
                              nfs_export_destroy='["nfs export destroy $export_name"]',
                              nfs_export_modify='["nfs export modify $export_name clients $clients options $export_options"]',
                              nfs_export_rename='["nfs export rename $export_name $new_export_name"]',
                              nfs_client_reset='["nfs reset clients"]',
                              nfs_restart='["nfs restart"]',
                              nfs_status='["nfs status"]'
                              )
    return conditions, supported_commands


def users():
    conditions = dict(
        user_add=dict(query=dict(state='add'), req_key=['user-name', 'user-password', 'dd-password', 'role-name'],
                      opt_key=['aging'], will_change=True, header=None),
        user_pass_change=dict(query=dict(state='change'),
                              req_key=['user-name', 'user-password', 'dd-password', 'new-password'], is_filter='user-name',
                              will_change=True, header=None),
        user_role_change=dict(query=dict(state='change'), req_key=['user-name', 'role-name'], will_change=True, header=None),
        user_enable=dict(query=dict(state='enable'), req_key=['user-name'], will_change=True, header=None),
        user_disable=dict(query=dict(state='disable'), req_key=['user-name'], will_change=True, header=None),
        user_del=dict(query=dict(state='del'), req_key=['user-name'], will_change=True, header=None),
        user_aging_set=dict(query=dict(state='set'), req_key=['aging', 'user-name'], will_change=True, header=None),
        user_aging_reset=dict(query=dict(state='reset'), req_key=['aging', 'user-name'], will_change=True, header=None),
        user_default_aging_set=dict(query=dict(state='set'), req_key=['aging'], will_change=True, header=None),
        user_default_aging_reset=dict(query=dict(state='reset'), req_key=['aging'], will_change=True, header=None),
        user_strength_set=dict(query=dict(state='set'), req_key=['strength'], will_change=True, header=None),
        user_strength_reset=dict(query=dict(state='reset'), req_key=['strength'], will_change=True, header=None),
        user_show_details=dict(query=dict(state='show'), req_key=['user-name'], will_change=False,
                               header=None),
        user_show=dict(query=dict(state='show'), req_key=[], will_change=False,
                       header=['name', 'uid', 'role', 'last_login_from', 'last_login_time',
                               'status', 'disable_date'])
        )

    supported_commands = dict(user_add='{"name": "$user_name", "role": "$role_name", "password": "$user_password"}',
                              user_pass_change='{"current_password": "$user_password", "new_password": "$new_password"}',
                              user_role_change='["user change role $user_name $role_name"]',
                              user_enable='["user enable $user_name"]',
                              user_disable='["user disable $user_name"]',
                              user_default_aging_reset='["user password aging option reset $aging"]',
                              user_aging_reset='["user password aging reset $user_name $aging"]',
                              user_default_aging_set='["user password aging option set $aging"]',
                              user_aging_set='["user password aging set $user_name $aging"]',
                              user_strength_set='["user password strength reset $strength"]',
                              user_strength_reset='["user password strength set $strength"]',
                              user_del='["user del $user_name"]',
                              user_show_details='["user show detailed $user_name"]',
                              user_show='["user show list"]'
                        )

    return conditions, supported_commands


def net():
    conditions = dict(
        net_aggregate_add=dict(query=dict(state='add', option='aggregate'),
                               req_key=['option', 'aggregate', 'virtual-ifname', 'physical-ifname'], will_change=True, header=None),
        net_aggregate_del=dict(query=dict(state='del', option='aggregate'),
                               req_key=['option', 'virtual-ifname', 'physical-ifname'], will_change=True, header=None),
        net_aggregate_modify=dict(query=dict(state='modify', option='aggregate'),
                                  req_key=['option', 'virtual-ifname', 'aggregate'], will_change=True, header=None),
        net_interface_config=dict(query=dict(state='config'),
                                  req_key=['ifname', 'ipaddr', 'netmask'], opt_key=['mtu'], will_change=True, header=None),
        net_interface_create=dict(query=dict(state='create'), req_key=['ifname'], opt_key=['vlan'], will_change=True, header=None),
        net_veth_create=dict(query=dict(state='create'), req_key=['vethid'], will_change=True, header=None),
        net_interface_destroy=dict(query=dict(state='destroy'), req_key=['ifname'], will_change=True, header=None),
        net_interface_enable=dict(query=dict(state='enable'), req_key=['ifname'], will_change=True, header=None),
        net_failover_add=dict(query=dict(state='add', option='failover'),
                              req_key=['option', 'virtual-ifname', 'ifname', 'failover'], will_change=True, header=None),
        net_failover_del=dict(query=dict(state='del', option='failover'),
                              req_key=['option', 'virtual-ifname', 'ifname'], will_change=True, header=None),
        net_failover_modify=dict(query=dict(state='modify', option='failover'),
                                 req_key=['option', 'virtual-ifname', 'failover'], will_change=True, header=None),
        net_hosts_add=dict(query=dict(state='add', option='hosts'), req_key=['option', 'host-list'], will_change=True, header=None),
        net_hosts_del=dict(query=dict(state='del', option='hosts'), req_key=['option', 'ipaddr'], will_change=True, header=None),
        net_hosts_reset=dict(query=dict(state='reset', option='hosts'), req_key=['option'], will_change=True, header=None),
        net_lookup_test=dict(query=dict(state='test', option='lookup'), req_key=['option'], will_change=False, header=None),
        net_ping_test=dict(query=dict(state='test', option='ping'), req_key=['option', 'ipaddr', 'count'], will_change=False, header=None),
        net_domainname_reset=dict(query=dict(state='reset', option='domainname'), req_key=['option'], will_change=True, header=None),
        net_searchdomains_reset=dict(query=dict(state='reset', option='searchdomains'), req_key=['option'],
                                     will_change=True, header=None),
        net_dns_reset=dict(query=dict(state='reset', option='dns'), req_key=['option'], will_change=True, header=None),
        net_hostname_reset=dict(query=dict(state='reset', option='hostname'), req_key=['option'], will_change=True, header=None),
        net_route_net_add=dict(query=dict(state='add', option='route', ),
                               req_key=['option', 'network', 'netmask', 'gateway', 'ifname'], will_change=True, header=None),
        net_route_host_add=dict(query=dict(state='add', option='route', ),
                                req_key=['option', 'ipaddr', 'gateway', 'ifname'], will_change=True, header=None),
        net_route_net_del=dict(query=dict(state='del', option='route'),
                               req_key=['option', 'network', 'netmask', 'gateway', 'ifname'], will_change=True, header=None),
        net_route_host_del=dict(query=dict(state='del', option='route'),
                                req_key=['option', 'ipaddr', 'gateway', 'ifname'], will_change=True, header=None),
        net_domainname_set=dict(query=dict(state='set', option='domainname'), req_key=['option', 'domainname'],
                                will_change=True, header=None),
        net_searchdomains_set=dict(query=dict(state='set', option='searchdomains'), req_key=['option', 'searchdomains'],
                                   will_change=True, header=None),
        net_dns_set=dict(query=dict(state='set', option='dns'), req_key=['option', 'dns'], will_change=True, header=None),
        net_hostname_set=dict(query=dict(state='set', option='hostname'), req_key=['option', 'hostname'],
                              will_change=True, header=None),
        net_settings_show=dict(query=dict(state='show'),
                               req_key=[], will_change=False, header=["port", "enabled", "state", "DHCP", "IP address", "netmask", "type", "additional_setting"]),
    )

    supported_commands = dict(
        net_aggregate_add='["net aggregate add $virtual_ifname interfaces $physical_ifname $aggregate"]',
        net_aggregate_del='["net aggregate del $virtual_ifname interfaces $physical_ifname"]',
        net_aggregate_modify='["net aggregate modify $virtual_ifname $aggregate"]',
        net_interface_config='["net config $ifname $ipaddr netmask $netmask"]',
        net_interface_create='["net create interface $ifname"]',
        net_veth_create='["net create virtual veth$vethid"]',
        net_interface_destroy='["net destroy $ifname"]',
        net_interface_enable='["net enable $ifname"]',
        net_failover_add='["net failover add $virtual_ifname interfaces $ifname $failover"]',
        net_failover_del='["net failover del $virtual_ifname interfaces $ifname"]',
        net_failover_modify='["net failover modify $virtual_ifname $failover"]',
        net_hosts_add='["net hosts add $host_list"]',
        net_hosts_del='["net hosts del $ipaddr"]',
        net_hosts_reset='["net hosts reset"]',
        net_lookup_test='["net lookup $ipaddr"]',
        net_ping_test='["net ping $ipaddr count $count"]',
        net_domainname_reset='["net reset domainname"]',
        net_searchdomains_reset='["net reset searchdomains"]',
        net_dns_reset='["net reset dns"]',
        net_hostname_reset='["net reset hostname"]',
        net_route_net_add='["net route add net $network netmask $netmask gw $gateway dev $ifname"]',
        net_route_host_add='["net route add host $ipaddr gw $gateway dev $ifname"]',
        net_route_net_del='["net route del net $network netmask $netmask gw $gateway dev $ifname"]',
        net_route_host_del='["net route del host $ipaddr gw $gateway dev $ifname"]',
        net_domainname_set='["net set domainname $domainname"]',
        net_searchdomains_set='["net set searchdomains $searchdomains"]',
        net_dns_set='["net set dns $dns"]',
        net_hostname_set='["net set hostname $hostname"]',
        net_settings_show='["net show settings"]',
        )
    return conditions, supported_commands


def mtree():
    conditions = dict(
        mtree_list=dict(query=dict(state='list'), req_key=[], will_change=False, header=['name', 'size', 'status']),
        mtree_alias_create=dict(query=dict(state='create'), req_key=['mtree-path', 'alias-name'], will_change=True, header=None),
        mtree_create=dict(query=dict(state='create'), req_key=['mtree-path'], opt_key=['quota', 'tenant-unit'],
                          will_change=True, header=None),
        mtree_alias_delete=dict(query=dict(state='delete'), req_key=['alias-name'], will_change=True, header=None),
        mtree_delete=dict(query=dict(state='delete'), req_key=['mtree-path'], will_change=True, header=None),
        mtree_rename=dict(query=dict(state='rename'), req_key=['mtree-path', 'new-mtree-path'], will_change=True, header=None),
        mtree_modify=dict(query=dict(state='modify'), req_key=['mtree-path', 'tenant-unit'], will_change=True, header=None),
        mtree_achoring_algo_set=dict(query=dict(state='set'), req_key=['mtree-path', 'anchoring-algorithm'],
                                     will_change=True, header=None),
        mtree_app_optimized_set=dict(query=dict(state='set'), req_key=['mtree-path', 'app-optimized-compression'],
                                     will_change=True, header=None),
        mtree_randomio_set=dict(query=dict(state='set'), req_key=['mtree-path', 'randomio'], will_change=True, header=None),
        mtree_achoring_algo_reset=dict(query=dict(state='reset'), req_key=['mtree-path', 'anchoring-algorithm'],
                                       will_change=True, header=None),
        mtree_app_optimized_reset=dict(query=dict(state='reset'), req_key=['mtree-path', 'app-optimized-compression'],
                                       will_change=True, header=None),
        mtree_randomio_reset=dict(query=dict(state='reset'), req_key=['mtree-path', 'randomio'], will_change=True, header=None),
        mtree_retention_lock_enable=dict(query=dict(state='enable'), req_key=['mtree-path', 'retention-lock'],
                                         will_change=True, header=None),
        mtree_retention_lock_disable=dict(query=dict(state='disable'), req_key=['mtree-path', 'retention-lock'],
                                          will_change=True, header=None),
        mtree_retention_lock_set=dict(query=dict(state='set'), req_key=['mtree-path', 'retention'],
                                      will_change=True, header=None),
        mtree_retention_lock_reset=dict(query=dict(state='reset'), req_key=['mtree-path', 'retention'],
                                        will_change=True, header=None),
        mtree_undelete=dict(query=dict(state='undelete'), req_key=['mtree-path'], will_change=True, header=None),
    )

    supported_commands = dict(mtree_alias_create='["mtree alias create $alias_name mtree $mtree_path"]',
                              mtree_create='["mtree create $mtree_path"]',
                              mtree_alias_delete='["mtree alias delete $alias_name"]',
                              mtree_delete='["mtree delete $mtree_path"]',
                              mtree_rename='["mtree rename $mtree_path $new_mtree_path"]',
                              mtree_modify='["mtree modify $mtree_path tenant-unit $tenant_unit"]',
                              mtree_achoring_algo_set='["mtree option set anchoring-algorithm $anchoring_algorithm mtree $mtree_path"]',
                              mtree_app_optimized_set='["mtree option set app-optimized-compression $app_optimized_compression mtree $mtree_path"]',
                              mtree_randomio_set='["mtree option set randomio $randomio mtree $mtree_path"]',
                              mtree_achoring_algo_reset='["mtree option reset anchoring-algorithm mtree $mtree_path"]',
                              mtree_app_optimized_reset='["mtree option reset app-optimized-compression mtree $mtree_path"]',
                              mtree_randomio_reset='["mtree option reset randomio mtree $mtree_path"]',
                              mtree_retention_lock_enable='["mtree retention-lock enable mode $retention_lock mtree $mtree_path"]',
                              mtree_retention_lock_disable='["mtree retention-lock disable mtree $mtree_path"]',
                              mtree_retention_lock_set='["mtree retention-lock set $retention mtree $mtree_path"]',
                              mtree_retention_lock_reset='["mtree retention-lock reset $retention mtree $mtree_path"]',
                              mtree_undelete='["mtree undelete $mtree_path"]',
                              mtree_list='["mtree list"]')

    return conditions, supported_commands


def filesys():
    conditions = dict(
        filesys_clean_reset=dict(query=dict(state='reset', operation='clean'), req_key=['operation', 'clean'],
                                 will_change=True, header=None),
        filesys_clean_set=dict(query=dict(state='set', operation='clean'), req_key=['operation', 'clean'], will_change=True, header=None),
        filesys_clean_start=dict(query=dict(state='start', operation='clean'), req_key=['operation'], will_change=True, header=None),
        filesys_clean_stop=dict(query=dict(state='stop', operation='clean'), req_key=['operation'], will_change=True, header=None),
        filesys_encryption_abort=dict(query=dict(state='abort-apply-changes', operation='encryption'), req_key=['operation'],
                                      will_change=True, header=None),
        filesys_encryption_apply=dict(query=dict(state='apply-changes', operation='encryption'), req_key=['operation'],
                                      will_change=True, header=None),
        filesys_encryption_ekmgr_set=dict(
            query=dict(state='set', operation='encryption', encryption='embedded-key-manager'),
            req_key=['operation', 'encryption', 'key-rotation-policy'], will_change=True, header=None),
        filesys_encryption_ekmgr_reset=dict(
            query=dict(state='reset', operation='encryption', encryption='embedded-key-manager'),
            req_key=['operation', 'encryption'],
            opt_key=['key-rotation-policy'], will_change=True, header=None),
        filesys_encryption_reset=dict(query=dict(state='reset', operation='encryption'), req_key=['operation', 'encryption'],
                                      opt_key=['key-rotation-policy'], will_change=True, header=None),
        filesys_encryption_km_ext_set=dict(query=dict(state='set', operation='encryption', encryption='key-manager'),
                                           req_key=['operation', 'encryption', 'external-key-manager'], will_change=True, header=None),
        filesys_encryption_km_krp_set=dict(query=dict(state='set', operation='encryption', encryption='key-manager'),
                                           req_key=['operation', 'encryption', 'key-rotation-policy'], will_change=True, header=None),
        filesys_encryption_algo_set=dict(query=dict(state='set', operation='encryption', encryption='algorithm'),
                                         req_key=['operation', 'encryption', 'algorithm'], will_change=True, header=None),
        filesys_encryption_create=dict(query=dict(state='create', operation='encryption'),
                                       req_key=['operation', 'encryption'], will_change=True, header=None),
        filesys_encryption_km_disable=dict(query=dict(state='disable', operation='encryption', encryption='key-manager'),
                                           req_key=['operation', 'encryption'], will_change=True, header=None),
        filesys_encryption_km_enable=dict(query=dict(state='enable', operation='encryption', encryption='key-manager'),
                                          req_key=['operation', 'encryption'], will_change=True, header=None),
        filesys_encryption_disable=dict(query=dict(state='disable', operation='encryption'),
                                        req_key=['operation'], opt_key=['tier'], will_change=True, header=None),
        filesys_encryption_enable=dict(query=dict(state='enable', operation='encryption'),
                                       req_key=['operation'], opt_key=['tier'], will_change=True, header=None),
        filesys_encryption_key_delete=dict(query=dict(state='delete', operation='encryption'),
                                           req_key=['operation'], opt_key=['key-id', 'muid', 'tier'], will_change=True, header=None),
        filesys_encryption_key_destroy=dict(query=dict(state='destroy', operation='encryption'),
                                            req_key=['operation'], opt_key=['key-id', 'muid', 'tier'],
                                            will_change=True, header=None),
        filesys_encryption_key_sync=dict(query=dict(state='sync', operation='encryption'),
                                         req_key=['operation'], will_change=True, header=None),
        filesys_fastcopy_create=dict(query=dict(state='create', operation='fastcopy'),
                                     req_key=['operation', 'fastcopy-source', 'fastcopy-destination'], will_change=True, header=None),
        filesys_enable=dict(query=dict(state='enable'), req_key=[], will_change=True, header=None),
        filesys_create=dict(query=dict(state='create'), req_key=[], will_change=True, header=None),
        filesys_clean_status=dict(query=dict(state='status', operation='clean'), req_key=['operation'], will_change=True, header=None),
        filesys_status=dict(query=dict(state='status'), req_key=[], will_change=True, header=None),

    )

    supported_commands = dict(filesys_enable='["filesys enable"]',
                              filesys_create='["filesys create"]',
                              filesys_clean_reset='["filesys clean reset $clean"]',
                              filesys_clean_set='["filesys clean set $clean"]',
                              filesys_clean_start='["filesys clean start"]',
                              filesys_clean_stop='["filesys clean stop"]',
                              filesys_encryption_abort='["filesys encryption abort-apply-changes"]',
                              filesys_encryption_apply='["filesys encryption apply-changes"]',
                              filesys_encryption_reset='["filesys encryption $encryption reset"]',
                              filesys_encryption_ekmgr_set='["filesys encryption embedded-key-manager set key-rotation-policy $key_rotation_policy"]',
                              filesys_encryption_km_ext_set='["filesys encryption key-manager set $external_key_manager"]',
                              filesys_encryption_km_krp_set='["filesys encryption key-manager set key-rotation-policy $key_rotation_policy"]',
                              filesys_encryption_algo_set='["filesys encryption algorithm set $algorithm"]',
                              filesys_encryption_ekmgr_reset='["filesys encryption embedded-key-manager reset key-rotation-policy"]',
                              filesys_encryption_create='["filesys encryption $encryption keys create"]',
                              filesys_encryption_km_disable='["filesys encryption key-manager disable"]',
                              filesys_encryption_km_enable='["filesys encryption key-manager enable"]',
                              filesys_encryption_disable='["filesys encryption disable"]',
                              filesys_encryption_enable='["filesys encryption enable"]',
                              filesys_encryption_key_delete='["filesys encryption keys delete"]',
                              filesys_encryption_key_destroy='["filesys encryption keys destroy"]',
                              filesys_encryption_key_sync='["filesys encryption keys sync"]',
                              filesys_clean_status='["filesys clean status"]',
                              filesys_fastcopy_create='["filesys fastcopy source $filecopy_source destination $filecopy_destination"]',
                              filesys_status='["filesys status"]')
    return conditions, supported_commands


def ddboost():
    conditions = dict(
        ddboost_storage_unit_create=dict(query=dict(state='create'), req_key=['storage-unit', 'user-name'],
                                         opt_key=['quota', 'stream-limit'], will_change=True, header=None),
        ddboost_storage_unit_delete=dict(query=dict(state='delete'), req_key=['storage-unit'], will_change=True, header=None),
        ddboost_storage_unit_modify=dict(query=dict(state='modify'), req_key=['storage-unit', 'user-name'],
                                         opt_key=['quota', 'stream-limit'], will_change=True, header=None),
        ddboost_storage_unit_rename=dict(query=dict(state='rename'), req_key=['storage-unit', 'new-storage-unit'],
                                         will_change=True, header=None),
        ddboost_storage_unit_undelete=dict(query=dict(state='undelete'), req_key=['storage-unit'], will_change=True, header=None),
        ddboost_user_assign=dict(query=dict(state='assign'), req_key=['user-name'], will_change=True, header=None),
        ddboost_user_unassign=dict(query=dict(state='unassign'), req_key=['user-name'], will_change=True, header=None),
        ddboost_status=dict(query=dict(state='status'), req_key=[], will_change=True, header=None),
        ddboost_enable=dict(query=dict(state='enable'), req_key=[], will_change=True, header=None),
        ddboost_disable=dict(query=dict(state='disable'), req_key=[], will_change=True, header=None),
    )

    supported_commands = dict(
        ddboost_storage_unit_create='["ddboost storage-unit create $storage_unit user $user_name"]',
        ddboost_storage_unit_delete='["ddboost storage-unit delete $storage_unit"]',
        ddboost_storage_unit_modify='["ddboost storage-unit modify $storage_unit user $user_name"]',
        ddboost_storage_unit_rename='["ddboost storage-unit rename $storage_unit $new_storage_unit"]',
        ddboost_storage_unit_undelete='["ddboost storage-unit undelete $storage_unit"]',
        ddboost_user_assign='["ddboost user assign $user_name"]',
        ddboost_user_unassign='["ddboost user unassign $user_name"]',
        ddboost_status='["ddboost status"]',
        ddboost_enable='["ddboost enable"]',
        ddboost_disable='["ddboost disable"]',
        )

    return conditions, supported_commands


def config():
    conditions = dict(
        config_adminemail_set=dict(query=dict(state='set'), req_key=['option', 'admin-email'], will_change=True, header=None),
        config_adminhost_set=dict(query=dict(state='set'), req_key=['option', 'admin-host'], will_change=True, header=None),
        config_location_set=dict(query=dict(state='set'), req_key=['option', 'location'], will_change=True, header=None),
        config_mailserver_set=dict(query=dict(state='set'), req_key=['option', 'mailserver'], will_change=True, header=None),
        config_timezone_set=dict(query=dict(state='set'), req_key=['option', 'timezone'], will_change=True, header=None),
        config_adminemail_reset=dict(query=dict(state='reset', option='admin-email'), req_key=['option'],
                                     will_change=True, header=None),
        config_adminhost_reset=dict(query=dict(state='reset', option='admin-host'), req_key=['option'],
                                    will_change=True, header=None),
        config_location_reset=dict(query=dict(state='reset', option='location'), req_key=['option'], will_change=True, header=None),
        config_mailserver_reset=dict(query=dict(state='reset', option='mailserver'), req_key=['option'],
                                     will_change=True, header=None),
        config_timezone_reset=dict(query=dict(state='reset', option='timezone'), req_key=['option'], will_change=True, header=None),
    )

    supported_commands = dict(config_adminemail_set='["config set admin-email $admin_email"]',
                              config_adminhost_set='["config set admin-host $admin_host"]',
                              config_location_set='["config set location $location"]',
                              config_mailserver_set='["config set mailserver $mailserver"]',
                              config_timezone_set='["config set timezone $timezone"]',
                              config_adminemail_reset='["config reset admin-email"]',
                              config_adminhost_reset='["config reset admin-mail"]',
                              config_location_reset='["config reset location"]',
                              config_mailserver_reset='["config reset mailserver"]',
                              config_timezone_reset='["config reset timezone"]',
                              )
    return conditions, supported_commands


def cifs():
    conditions = dict(
        cifs_share_create=dict(query=dict(state='create'), req_key=['share'], 
                    opt_key=['path', 'max-connections', 'clients', 'users'], will_change=True, header=None),
        cifs_share_modify=dict(query=dict(state='modify'), req_key=['share'], 
                opt_key=['max-connections', 'clients', 'users'], will_change=True, header=None),
        cifs_share_destroy=dict(query=dict(state='destroy'), req_key=['share'], will_change=True, header=None),
        cifs_share_disable=dict(query=dict(state='disable'), req_key=['share'], will_change=True, header=None),
        cifs_share_enable=dict(query=dict(state='enable'), req_key=['share'], will_change=True, header=None), 
        cifs_share_show=dict(query=dict(state='show'), req_key=['share'], will_change=False, header=None),
        cifs_config_show=dict(query=dict(state='show'), req_key=[], will_change=False, header=None),
        cifs_enable=dict(query=dict(state='enable'), req_key=[], will_change=True, header=None),
        cifs_disable=dict(query=dict(state='disable'), req_key=[], will_change=True, header=None),
        cifs_status=dict(query=dict(state='status'), req_key=[], will_change=False, header=None),
    )

    supported_commands = dict(cifs_enable='["cifs enable"]',
                              cifs_disable='["cifs disable"]',
                              cifs_status='["cifs status"]',
                              cifs_share_create='["cifs share create $share"]',
                              cifs_share_modify='["cifs share modify $share"]',
                              cifs_share_destroy='["cifs share destroy $share"]',
                              cifs_share_disable='["cifs share disable $share"]',
                              cifs_share_enable='["cifs share enable $share"]',
                              cifs_share_show='["cifs share show $share"]',
                              cifs_config_show='["cifs show config"]',
                              )

    return conditions, supported_commands


def adminaccess():
    conditions = dict(
        adminAccess_enable=dict(query=dict(state='enable'), req_key=['service'], will_change=True, header=None),
        adminAccess_disable=dict(query=dict(state='disable'), req_key=['service'], will_change=True, header=None),
        adminAccess_show=dict(query=dict(state='show'), req_key=[], will_change=False, header=None),
    )

    supported_commands = dict(adminAccess_enable='["adminaccess enable $service"]',
                              adminAccess_disable='["adminaccess disable $service"]',
                              adminAccess_show='["adminaccess show"]',
                             )

    return conditions, supported_commands


def compression():
    conditions = dict(
        compression_schedule_enable=dict(query=dict(state='enable'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_disable=dict(query=dict(state='disable'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_destroy=dict(query=dict(state='destroy'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_modify=dict(query=dict(state='modify'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_del=dict(query=dict(state='del'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_create=dict(query=dict(state='create'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_add=dict(query=dict(state='add'), req_key=['schedule'], will_change=True, header=None),
        compression_schedule_show=dict(query=dict(state='show'), req_key=['schedule'], will_change=False, header=None),
        compression_sample_stop=dict(query=dict(state='stop'), req_key=['sample'], will_change=True, header=None),
        compression_sample_start=dict(query=dict(state='start'), req_key=['sample'], will_change=True, header=None),
        compression_throttle_set=dict(query=dict(state='set'), req_key=['throttle'], will_change=True, header=None),
        compression_throttle_reset=dict(query=dict(state='reset'), req_key=['throttle'], will_change=True, header=None),
        compression_throttle_show=dict(query=dict(state='show'), req_key=['throttle'], will_change=False, header=None),
        compression_status=dict(query=dict(state='status'), req_key=[], will_change=False, header=None),
        compression_enable_initialize=dict(query=dict(state='enable'), req_key=['initialize'], will_change=True, header=None),
        compression_enable=dict(query=dict(state='enable'), req_key=[], will_change=True, header=None),
        compression_disable=dict(query=dict(state='disable'), req_key=[], will_change=True, header=None),

    )
    supported_commands = dict(compression_schedule_enable='["compression physical-capacity-measurement schedule enable $schedule"]',
                              compression_schedule_disable='["compression physical-capacity-measurement schedule disable $schedule"]',
                              compression_status='["compression physical-capacity-measurement status"]',
                              compression_schedule_destroy='["compression physical-capacity-measurement schedule destroy $schedule"]',
                              compression_schedule_modify='["compression physical-capacity-measurement schedule modify $schedule"]',
                              compression_schedule_del='["compression physical-capacity-measurement schedule del $schedule"]',
                              compression_schedule_create='["compression physical-capacity-measurement schedule create $schedule"]',
                              compression_schedule_add='["compression physical-capacity-measurement schedule add $schedule"]',
                              compression_schedule_show='["compression physical-capacity-measurement schedule show $schedule"]',
                              compression_sample_stop='["compression physical-capacity-measurement sample stop $sample"]',
                              compression_sample_start='["compression physical-capacity-measurement sample start $sample"]',
                              compression_throttle_set='["compression physical-capacity-measurement throttle set $throttle"]',
                              compression_throttle_reset='["compression physical-capacity-measurement throttle reset"]',
                              compression_throttle_show='["compression physical-capacity-measurement throttle show"]',
                              compression_enable = '["compression physical-capacity-measurement enable"]',
                              compression_disable = '["compression physical-capacity-measurement disable"]',
                              compression_enable_initialize='["compression physical-capacity-measurement enable and-initialize"]'
                              )

    return conditions, supported_commands
