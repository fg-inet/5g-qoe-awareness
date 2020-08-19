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

network simpleNHost1ServerLinkUtilizationTest
{
    parameters:
        @display("bgb=710,417");
        int numStandardHosts = default(1);
    types:
        channel C extends DatarateChannel
        {
        }
    submodules:
        configurator: Ipv4NetworkConfigurator {
            @display("p=10,10;is=s");
        }
        stdHost[numStandardHosts]: StandardHost {

        }
        router0: Router {
            @display("p=233,203");
        }
        router1: Router {
            @display("p=438,203");
        }
        visualizer: IntegratedVisualizer {
            @display("p=18,71");
        }
        server: StandardHost {
            @display("p=560,203");
        }
    connections:
        router0.pppg++ <--> conn1: C { datarate = 100Mbps; } <--> router1.pppg++;

        for i=0..numStandardHosts-1 {
            stdHost[i].pppg++ <--> C {  datarate = 1Gbps; delay = 100ns; } <--> router0.pppg++;
        }
        server.pppg++ <--> C {  datarate = 10Gbps; delay = 100ns; } <--> router1.pppg++;
}
