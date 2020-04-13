#!/usr/bin/python
"""
to prepare the code I've used examples and descriptions from 
https://osrg.github.io/ryu-book/en/html/spanning_tree.html
https://inside-openflow.com/2016/06/29/custom-mininet-topologies-and-introducing-atom/
http://mininet.org/api/hierarchy.html
"""
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import RemoteController, OVSSwitch

class BasicTopo( Topo ):
    "Simple test topology"
    

    def build( self,noOfRacks=3, noOfHost=2  ):
        myList=[]
        myList.append(dict(bw=100, delay='0ms', max_queue_size=1000, use_htb=True))
        myList.append(dict(bw=50, delay='5ms', max_queue_size=1000, use_htb=True))
        myList.append(dict(bw=33, delay='10ms', max_queue_size=1000, use_htb=True))
        myList.append(dict(bw=25, delay='15ms', max_queue_size=1000, use_htb=True))

        self.racks = []
        mainS= []
    #check if no of racks is in 1-4 range
        if noOfRacks > 4:
            raise Exception( "Max 4 Racks supported!" )

        if noOfHost > 8:
            raise Exception( "Max 8 Hosts per Rack supported!" )    
        
#1 root switches. This should be the same as no of racks
        for i in range(noOfRacks):
            rootSwitch = self.addSwitch( 's%s' % (i+1) )
            mainS.append( rootSwitch )
#2 connect all root switches
            if i > 0:
                self.addLink( lastS, rootSwitch )
            lastS=rootSwitch

        if len(mainS)>1:
                self.addLink( lastS, mainS[0] )
#3 racks        
        for i in irange( 1, noOfRacks ):
            rack = self.buildRack( i ,noOfHost=noOfHost,
                                   myList=myList )
            self.racks.append( rack )
                
            #for z in range (noOfRacks):
            for switch in rack:
                self.addLink( mainS[i-1], switch )


    def buildRack( self, noR, noOfHost,  myList ):
        "Build a rack of hosts with a top-of-rack switch"
        dpid = ( noR * 16 ) + 1
        #switch = self.addSwitch( 's1r%s' % loc, dpid='%x' % dpid )
        switch = self.addSwitch( 's1r%s' % noR, dpid='%x' % dpid)
#2 hosts per rack
        for n in irange( 1, noOfHost ):
            host = self.addHost( 'h%sr%s' % ( n, noR ) )
            self.addLink( switch, host, **myList[noR-1] )

        # Return list of top-of-rack switches for this rack
        return [switch]

def runT1():
    "Bootstrap a Mininet network using the Minimal Topology"
    # Create an instance of the topology
    topo = BasicTopo()

    # Create a network based on the topology using OVS and controlled by
    # a remote controller.
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController( name, ip='127.0.0.1' ),
        switch=OVSSwitch,
        autoSetMacs=True,
        link=TCLink )

    # Actually start the network
    net.start()

    # Drop the user in to a CLI so user can run commands.
    CLI( net )

    # After the user exits the CLI, shutdown the network.
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    runT1()

# Allows the file to be imported using mn option 
topos = {
    'dcbasic': BasicTopo
}
