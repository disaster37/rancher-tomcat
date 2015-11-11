FROM webcenter/rancher-stack-base:latest
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>

ENV TOMCAT_BRANCH 8
ENV TOMCAT_VERSION 8.0.28

# Force Tomcat to bind on IPV4
ENV _JAVA_OPTIONS -Djava.net.preferIPv4Stack=true

# Install JDK 8
RUN \
echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
add-apt-repository -y ppa:webupd8team/java && \
apt-get update && \
apt-get install -y oracle-java8-installer tar && \
rm -rf /var/cache/oracle-jdk8-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

# Get Tomcat
RUN wget --quiet --no-cookies http://apache.rediris.es/tomcat/tomcat-${TOMCAT_BRANCH}/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz -O /tmp/tomcat.tgz

# Uncompress
RUN tar xzvf /tmp/tomcat.tgz -C /opt
RUN mv /opt/apache-tomcat-${TOMCAT_VERSION} /opt/tomcat
RUN rm /tmp/tomcat.tgz

# Remove garbage
RUN rm -rf /opt/tomcat/webapps/examples
RUN rm -rf /opt/tomcat/webapps/docs
RUN rm -rf /opt/tomcat/webapps/ROOT

ENV CATALINA_HOME /opt/tomcat
ENV PATH $PATH:$CATALINA_HOME/bin

# Add account
RUN groupadd tomcat
RUN useradd -s /bin/false -g tomcat -d /opt/tomcat tomcat
RUN chown -R tomcat:tomcat /opt/tomcat

# Add main script
ADD assets/setup/supervisor-tomcat.conf /etc/supervisor/conf.d/tomcat.conf
ADD assets/init.py /app/init.py
ADD assets/run /app/run
RUN chmod 755 /app/init.py
RUN chmod 755 /app/run
RUN touch /firstrun

EXPOSE 8080
EXPOSE 8009
VOLUME "/opt/tomcat/webapps"
WORKDIR /opt/tomcat

# Launch Tomcat
CMD ["/app/run"]

