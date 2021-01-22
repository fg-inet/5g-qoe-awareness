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

package inet.applications.generic;

simple linkAdjuster
{
	parameters:
        double adjustmentInterval @unit(s) = default(10s);
        int numSlices = default(2); // 2 or 5 supported with specific link and host names, as well as specific mos value signal names
        string lvdAs = default("BWS"); // Live video client as bandwidth (BWS) or delay (DES) sensitive application. Only relevant for 2 slices
        
        @signal[setBWSbitrate](type="double");
        @statistic[setBWSbitrate](title="Bitrate set for bandwidth sensitive slice"; record=vector);
        @signal[setDESbitrate](type="double");
        @statistic[setDESbitrate](title="Bitrate set for delay sensitive slice"; record=vector);
        @signal[meanBWSmos](type="double");
        @statistic[meanBWSmos](title="Mean bandwidth sensitive clients mos for last time period"; record=vector);
        @signal[meanDESmos](type="double");
        @statistic[meanDESmos](title="Mean delay sensitive clients mos for last time period"; record=vector);
        @signal[mosDifference](type="double");
        @statistic[mosDifference](title="meanBWSmos - meanDESmos"; record=vector);
}