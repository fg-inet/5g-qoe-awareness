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

#include "inet/common/INETDefs.h"
#include "inet/common/INETMath.h"

#include "mosListener.h"

#ifndef INET_APPLICATIONS_GENERIC_LINKADJUSTER_H_
#define INET_APPLICATIONS_GENERIC_LINKADJUSTER_H_

namespace inet {

class INET_API linkAdjuster: public cSimpleModule {
public:
    linkAdjuster();
    virtual ~linkAdjuster();
protected:
    virtual int numInitStages() const override { return NUM_INIT_STAGES; }
    cMessage *timeoutMsg = nullptr;

    simtime_t adjustmentInterval;
    int numSlices;
    std::string lvdAs;

    simsignal_t setBWSbitrateSignal;
    simsignal_t setDESbitrateSignal;
    simsignal_t meanBWSmosSignal;
    simsignal_t meanDESmosSignal;
    simsignal_t mosDifferenceSignal;

    simtime_t lastAdjustment;

    mosListener *sshListener;
    mosListener *voipListener;
    mosListener *liveVideoListener;
    mosListener *vodListener;
    mosListener *fileDownloadListener;

    std::list<mosListener*> bwsListeners;
    std::list<mosListener*> desListeners;

    virtual void initialize(int stage) override;
    virtual void handleMessage(cMessage *msg) override;

    std::list<cChannel*> connChannels;

    std::list<cChannel*> getChannelFromName(const char* linkName);
    std::list<cChannel*> getConnLinks();
    void setLinkBitrateByLinkName(const char* linkName, double targetBitrate);
    double setLinkBitrate(cChannel *channel, double targetBitrate);
    double getLinkBitrate(cChannel *channel);

    std::map<std::string, double> calculateMeanClientMos(mosListener *listener, simtime_t considerStartTime);
    double calculateMeanMosRAClass(std::list<mosListener*> appListeners, simtime_t considerStartTime);
    void twoSliceAlgorithm();
};

} /* namespace inet */

#endif /* INET_APPLICATIONS_GENERIC_LINKADJUSTER_H_ */
