#https://stackoverflow.com/questions/34366499/ldap3-python-search-members-of-a-group-and-retrieve-their-samacountname-active

import logging
import json

from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, BASE, ALL_ATTRIBUTES, ObjectDef, AttrDef, Reader, Entry, Attribute, OperationalAttribute, ALL
from flask import Flask, jsonify, Response, make_response
from waitress import serve

#from uldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE, BASE, ALL_ATTRIBUTES, ObjectDef, AttrDef, Reader, Entry, Attribute, OperationalAttribute, ALL
app = Flask(__name__)

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')

@app.route('/', methods=['GET'])
def Cache_AD_Group_Members():
    address= 'dms.local'
    dn='DC=dms,DC=local'
    user='supersecretuser@domain'
    password=''
    group_name= '3D Printing Basics'

    server = Server(address, get_info=ALL,mode='IP_V4_PREFERRED')
    conn = Connection(server, user, password, auto_bind=True, )
    members = []
    AD_GROUP_FILTER = '(&(objectClass=GROUP)(cn={group_name}))'
    ad_filter = AD_GROUP_FILTER.replace('{group_name}', group_name)    

    #conn.search('OU details', ad_filter, search_scope=SUBTREE, attributes=['employeeID'])

    conn.search(
        search_base='CN=3D Printer Basics,OU=Security,OU=Groups,DC=dms,DC=local',
        search_filter='(objectClass=group)',
        search_scope='SUBTREE',
        attributes = ['cn', 'member']
    )

    group_members=conn.entries[0].member.values
    print(str(len(group_members)) + " total members in group")

    user_list=[]

    for member in group_members:
        try: 
            conn.search(
                search_base='OU=Members,DC=dms,DC=local',
                search_filter=f'(&(distinguishedName={member}))', #TODO: filter out disabled accounts (useraccountcontrol==514) and ADM accounts
                attributes=['cn','employeeID','userAccountControl']
            )
            #print(conn.entries[0].upn.values)
            #print(type(conn.entries[0].cn.values[0]))
            if conn.entries[0].userAccountControl.values[0] == 512:
                user_dict = {'cn' : conn.entries[0].cn.values, 'employeeID' : conn.entries[0].employeeID.values}
                user_list.append(user_dict)

        except Exception as e:
            logging.warning('issue on ' + member + ' ' + str(e))
            print('issue on ' + member + ' ' + str(e))
    
    with app.app_context():
        return make_response(jsonify(user_list))

json_list = Cache_AD_Group_Members()

print("Cache Generated")

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80)

