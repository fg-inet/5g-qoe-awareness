//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

package _5gns.simulations;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.Router;
import inet.node.inet.StandardHost;
import inet.visualizer.integrated.IntegratedVisualizer;
import inet.visualizer.linklayer.InterfaceTableVisualizer;
import ned.DatarateChannel;
import inet.node.internetcloud.InternetCloud;

network simple4HostTestNet
{
    @display("bgb=710,417");
    types:
        channel C extends DatarateChannel
        {
//            delay = 1ns;
        }
    submodules:
        configurator: Ipv4NetworkConfigurator {
            @display("p=10,10;is=s");
        }
        stdHost0: StandardHost {
            @display("p=115,62");
        }
        stdHost1: StandardHost {
            @display("p=115,153");
        }
        stdHost2: StandardHost {
            @display("p=115,252");
        }
        stdHost3: StandardHost {
            @display("p=115,347");
        }
        router0: Router {
            @display("p=233,203");
        }
        router1: Router {
            @display("p=438,203");
        }
//        etherHub: Router {
//            @display("p=332,170");
//        }
//        etherHub1: Router {
//            @display("p=332,231");
//        }
        visualizer: IntegratedVisualizer {
            @display("p=18,71");
        }
        server0: StandardHost {
            @display("p=562,71");
        }
        server1: StandardHost {
            @display("p=562,153");
        }
        server2: StandardHost {
            @display("p=562,252");
        }
        server3: StandardHost {
            @display("p=562,347");
        }
    connections:
//        router0.pppg++ <--> C {datarate = 50Mbps;} <--> etherHub.pppg++;
//        etherHub.pppg++ <--> C {datarate = 50Mbps;} <--> router1.pppg++;
//        router0.pppg++ <--> C {datarate = 100Mbps;} <--> etherHub1.pppg++;
//        etherHub1.pppg++ <--> C {datarate = 100Mbps;} <--> router1.pppg++;
		
		router0.pppg++ <--> C {datarate = 50Mbps; delay = 10ms;} <--> router1.pppg++;
		router0.pppg++ <--> C {datarate = 100Mbps; delay = 10ms;} <--> router1.pppg++;
		
        stdHost0.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router0.pppg++;
        stdHost1.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router0.pppg++;
        stdHost2.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router0.pppg++;
        stdHost3.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router0.pppg++;
        
        server0.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router1.pppg++;
        server1.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router1.pppg++;
        server2.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router1.pppg++;
        server3.pppg++ <--> C {datarate = 1Gbps; delay = 1ns;} <--> router1.pppg++;
}
