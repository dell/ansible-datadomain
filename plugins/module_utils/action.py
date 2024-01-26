
def cifs(status):
    if status:
        conditions = dict(
            cifs_share_modify_add=dict(query=dict(state='present'), req_key=['share'], 
                    opt_key=['max-connections', 'clients', 'users', 'disable', 'groups'], will_change=True, header=None),

            cifs_share_modify_del=dict(query=dict(state='absent'), req_key=['share'], 
                    opt_key=['max-connections', 'clients', 'users', 'disable', 'groups'], will_change=True, header=None),
        )
    else:
        conditions = dict(
            cifs_share_create=dict(query=dict(state='present'), req_key=['share'], 
                        opt_key=['max-connections', 'clients', 'users', 'groups'], will_change=True, header=None,
                        check_status_ep='/rest/v1.0/dd-systems/0/protocols/cifs/shares'),

            cifs_share_modify=dict(query=dict(state='absent'), req_key=['share'], 
                    opt_key=['max-connections', 'clients', 'users', 'disable', 'groups'], will_change=True, header=None, 
                    check_status_ep='/rest/v1.0/dd-systems/0/protocols/cifs/shares'),

            cifs_enable=dict(query=dict(state='present'), req_key=[], will_change=True, header=None, 
                check_status_ep='/api/v1/dd-systems/0/protocols/cifs/status'),
            cifs_disable=dict(query=dict(state='absent'), req_key=[], will_change=True, header=None, 
                check_status_ep='/api/v1/dd-systems/0/protocols/cifs/status'),
        
    )

    payload = dict(cifs_enable='/api/v1/dd-systems/0/protocols/cifs/enable',
                   cifs_disable='/api/v1/dd-systems/0/protocols/cifs/disable',
                   cifs_share_create='/rest/v1.0/dd-systems/0/protocols/cifs/shares',
                   cifs_share_modify_add='/rest/v1.0/dd-systems/{SYSTEM-ID}/protocols/cifs/shares',
                   cifs_share_modify_del='/rest/v1.0/dd-systems/{SYSTEM-ID}/protocols/cifs/shares'
                
                 )
    return conditions, payload


def adminaccess():
    conditions = dict(
        adminaccess_enable_service=dict(query=dict(state='present'), req_key=['service'], opt_key=[], will_change=True, header=None),
        adminaccess_disable_service=dict(query=dict(state='absent'), req_key=['service'], opt_key=[], will_change=True, header=None)
    )

    payload = dict(adminaccess_enable_service='adminaccess enable',
    adminaccess_disable_service='adminaccess disable'
    )

    return conditions, payload


