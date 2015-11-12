#!/usr/bin/python
import os
import re
import shutil
import sys
import time
from rancher_metadata import MetadataAPI

__author__ = 'Sebastien LANGOUREAUX'

TOMCAT_PATH = '/opt/tomcat'

class ServiceRun():



  def run(self):

    # We put tomcat on original state or if it's first run, we copy the original config
    self.__do_tomcat_original_setting()

    while True:
        try:
            status = self.__set_tomcat_cluster()
            if status == True:
                break
        except Exception,e:
            print("Some error appear : " + e.message)

        print("We try again in 60s")
        time.sleep(60)

    print("Setting done")



  def __set_tomcat_user(self):

    print("@todo")

  def __do_tomcat_original_setting(self):
      global TOMCAT_PATH

      # All other run
      if os.path.isfile(TOMCAT_PATH + '/conf/server.xml.org'):
          shutil.copy2(TOMCAT_PATH + '/conf/server.xml.org', TOMCAT_PATH + '/conf/server.xml')
          shutil.copy2(TOMCAT_PATH + '/conf/context.xml.org', TOMCAT_PATH + '/conf/context.xml')

      # First run
      else:
          shutil.copy2(TOMCAT_PATH + '/conf/server.xml', TOMCAT_PATH + '/conf/server.xml.org')
          shutil.copy2(TOMCAT_PATH + '/conf/context.xml', TOMCAT_PATH + '/conf/context.xml')


  def __set_tomcat_cluster(self):
    global TOMCAT_PATH

    metadata_manager = MetadataAPI()

    # I check there are more than 1 container
    number_node = metadata_manager.get_service_scale_size()
    if number_node < 2 :
        print("No cluster setting needed")
        return True

    print("We will setting Tomcat cluster with " + str(number_node) + " instances")

    # I get my container info
    my_name = metadata_manager.get_container_name()
    my_ip = metadata_manager.get_container_ip()
    my_id = metadata_manager.get_container_id()

    # I get the other container info
    list_containers = {}
    list_containers_name = metadata_manager.get_service_containers()
    for container_name in list_containers_name:
        if container_name != my_name:
            list_containers[container_name] = {}
            list_containers[container_name]['id'] = metadata_manager.get_container_id(container_name)
            list_containers[container_name]['name'] = container_name
            list_containers[container_name]['ip'] = metadata_manager.get_container_ip(container_name)
            if list_containers[container_name]['ip'] is None or list_containers[container_name]['ip'] == '':
                print("The container " + container_name + " have not yet the IP. We stay it")
                return False

    # We set the engine name
    self.replace_all(TOMCAT_PATH + '/conf/server.xml', re.escape('<Engine name="Catalina" defaultHost="localhost">'), '<Engine name="Catalina" defaultHost="localhost" jvmRoute="' + my_name + '">')

    # We set the cluster
    cluster_setting = '''
    <Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster" channelSendOptions="6" channelStartOptions="3">

        <Channel className="org.apache.catalina.tribes.group.GroupChannel">

            <Receiver className="org.apache.catalina.tribes.transport.nio.NioReceiver" autoBind="0" selectorTimeout="5000" maxThreads="6" address="''' + my_ip + '''" port="4444" />
                <Sender className="org.apache.catalina.tribes.transport.ReplicationTransmitter">
                    <Transport className="org.apache.catalina.tribes.transport.nio.PooledParallelSender" timeout="60000" keepAliveTime="10" keepAliveCount="0" />
                </Sender>
                <Interceptor className="org.apache.catalina.tribes.group.interceptors.TcpPingInterceptor"/>
                <Interceptor className="org.apache.catalina.tribes.group.interceptors.TcpFailureDetector"/>
                <Interceptor className="org.apache.catalina.tribes.group.interceptors.MessageDispatch15Interceptor"/>
                <Interceptor className="org.apache.catalina.tribes.group.interceptors.StaticMembershipInterceptor">'''

    for container in list_containers.itervalues():
        cluster_setting += '<Member className="org.apache.catalina.tribes.membership.StaticMember" host="' + container['ip'] + '" port="4444" uniqueId="{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,' + str(container['id']) + '}"/>'
    cluster_setting += '''
                </Interceptor>
        </Channel>
        <Valve className="org.apache.catalina.ha.tcp.ReplicationValve" filter="" />
        <Valve className="org.apache.catalina.ha.session.JvmRouteBinderValve"/>
        <ClusterListener className="org.apache.catalina.ha.session.ClusterSessionListener"/>
    </Cluster>
    '''
    self.replace_all(TOMCAT_PATH + '/conf/server.xml', re.escape('</Host>'), cluster_setting + "\n" + '</Host>')

    self.replace_all(TOMCAT_PATH + '/conf/context.xml', re.escape('</Context>'), '<Manager className="org.apache.catalina.ha.session.DeltaManager" expireSessionsOnShutdown="false" notifyListenersOnReplication="true" /></Context>')

    return True




  def replace_all(self, file, searchRegex, replaceExp):
    """ Replace String in file with regex
    :param file: The file name where you should to modify the string
    :param searchRegex: The pattern witch must match to replace the string
    :param replaceExp: The string replacement
    :return:
    """

    regex = re.compile(searchRegex, re.IGNORECASE)

    f = open(file,'r')
    out = f.readlines()
    f.close()

    f = open(file,'w')

    for line in out:
      if regex.search(line) is not None:
        line = regex.sub(replaceExp, line)

      f.write(line)

    f.close()


  def add_end_file(self, file, line):
    """ Add line at the end of file
    :param file: The file where you should to add line to the end
    :param line: The line to add in file
    :return:
    """
    with open(file, "a") as myFile:
        myFile.write("\n" + line + "\n")



if __name__ == '__main__':
    # Start
    if(len(sys.argv) > 1 and sys.argv[1] == "start"):

        service = ServiceRun()
        service.run()


