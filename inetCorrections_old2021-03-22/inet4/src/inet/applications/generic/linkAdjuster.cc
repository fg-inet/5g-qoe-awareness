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

#include "linkAdjuster.h"

#include <string.h>

#include "inet/common/ModuleAccess.h"
#include "inet/common/ProtocolGroup.h"
#include "inet/common/ProtocolTag_m.h"
#include "inet/common/TimeTag_m.h"
#include "inet/common/lifecycle/ModuleOperations.h"

namespace inet {

    #define MSGKIND_ADJUSTRATE    0

    Define_Module(linkAdjuster);

    linkAdjuster::linkAdjuster() {
        connChannels = getConnLinks();
    }

    linkAdjuster::~linkAdjuster() {
        cancelAndDelete(timeoutMsg);
    }

    std::list<cChannel*> linkAdjuster::getChannelFromName(const char* linkName) {
        std::list<cChannel*>::iterator it;
        std::list<cChannel*> channelsWithName;
        for (it = connChannels.begin(); it != connChannels.end(); ++it){
            int nameLength = std::strlen(linkName); //Can be a partial name!
            cChannel* mod = *it;
            if (std::strncmp(linkName, mod->getName(), nameLength) == 0) {
                channelsWithName.push_back(mod);
            }
        }
        return channelsWithName;
    }

    void linkAdjuster::initialize(int stage) {
        if (stage == INITSTAGE_LOCAL) {
            EV << "Initialize of the link adjuster module!" << endl;

            connChannels = getConnLinks();
            adjustmentInterval = par("adjustmentInterval");
            numSlices = par("numSlices");
            lvdAs = par("lvdAs").stringValue();
            lastAdjustment = simTime();

            setBWSbitrateSignal = registerSignal("setBWSbitrate");
            emit(setBWSbitrateSignal, getLinkBitrate(getChannelFromName("connBWS").front()));
            setDESbitrateSignal = registerSignal("setDESbitrate");
            emit(setDESbitrateSignal, getLinkBitrate(getChannelFromName("connDES").front()));
            meanBWSmosSignal = registerSignal("meanBWSmos");
            meanDESmosSignal = registerSignal("meanDESmos");
            mosDifferenceSignal = registerSignal("mosDifference");

            timeoutMsg = new cMessage("timer");
            simtime_t now = simTime();
            timeoutMsg->setKind(MSGKIND_ADJUSTRATE);
            scheduleAt(now + adjustmentInterval, timeoutMsg);
        } else if (stage == INITSTAGE_LAST) {
            sshListener = new mosListener();
            voipListener = new mosListener();
            liveVideoListener = new mosListener();
            vodListener = new mosListener();
            fileDownloadListener = new mosListener();
            EV << "linkAdjuster: Parent module = " << getSimulation()->getSystemModule()->getFullName() << "\n";
            getSimulation()->getSystemModule()->subscribe("mosValue", sshListener);
            getSimulation()->getSystemModule()->subscribe("voipMosRate", voipListener);
            getSimulation()->getSystemModule()->subscribe("DASHliveMosScore", liveVideoListener);
            getSimulation()->getSystemModule()->subscribe("DASHmosScore", vodListener);
            getSimulation()->getSystemModule()->subscribe("mosScore", fileDownloadListener);
            bwsListeners.push_back(vodListener);
            bwsListeners.push_back(fileDownloadListener);
            desListeners.push_back(sshListener);
            desListeners.push_back(voipListener);
            if (numSlices == 2) {
                EV << "linkAdjuster: 2 slices selected" << endl;

                if (lvdAs == "BWS") {
                    bwsListeners.push_back(liveVideoListener);
                } else if (lvdAs == "DES") {
                    desListeners.push_back(liveVideoListener);
                } else {
                    EV << "linkAdjuster: something wrong" << endl;
                    throw cRuntimeError("Invalid liveVideoClassifier: %s", lvdAs);
                }
            }

        }

    }

    double linkAdjuster::getLinkBitrate(cChannel *channel) {
        EV << "Channel \"" << channel->getName() << "\" with id: " << channel->getId() << endl;
        cPar& datarateParameter = channel->par("datarate");
        double datarate = datarateParameter.doubleValue();
        EV << "\tDatarate = " << datarate << " " << datarateParameter.getUnit() << endl;
        return datarate;
    }

    double linkAdjuster::setLinkBitrate(cChannel *channel, double targetBitrate) {
        EV << "Channel \"" << channel->getName() << "\" with id: " << channel->getId() << endl;
        cPar& datarateParameter = channel->par("datarate");
        EV << "\tDatarate - before = " << datarateParameter.doubleValue() << " " << datarateParameter.getUnit() << endl;
        datarateParameter.setDoubleValue(targetBitrate);
        EV << "\tDatarate - after =  " << datarateParameter.doubleValue() << " " << datarateParameter.getUnit() << endl;
        return datarateParameter.doubleValue();
    }

    void linkAdjuster::setLinkBitrateByLinkName(const char* linkName, double targetBitrate) {
        std::list<cChannel*> channelsToSet = getChannelFromName(linkName);
        std::list<cChannel*>::iterator it;
        for (it = channelsToSet.begin(); it != channelsToSet.end(); ++it){
            cChannel* mod = *it;
            setLinkBitrate(mod, targetBitrate);
        }
    }

    std::list<cChannel*> linkAdjuster::getConnLinks() {
        cModule *system = cSimulation::getActiveSimulation()->getSystemModule();
        std::list<cChannel*>::iterator it;
        std::list<cChannel*> channelList;
        for (ChannelIterator it(system); !it.end(); ++it) {
            cChannel * mod = *it;
            if (strncmp("conn", mod->getName(), 4) == 0) {
                channelList.push_back(mod);
            }
        }
        return channelList;
    }

    std::map<std::string, double> linkAdjuster::calculateMeanClientMos(mosListener *listener, simtime_t considerStartTime) {
        std::map<std::string, std::list<std::pair<simtime_t, double>>> mosValues = listener->allMos;
        std::map<std::string, double> meanMosPerClient;
        double slope = 1.0;
        if (listener == sshListener) {
            slope = 4.0 / 3.29795;
        } else if (listener == voipListener) {
            slope = 4.0 / 3.40363;
        } else if (listener == liveVideoListener || listener == vodListener) {
            slope = 4.0 / 3.5857;
        }
        for (auto const& clientEntry : mosValues) {
            std::string clientName = clientEntry.first;
            double cumulatedValidMos = 0.0;
            double numValidEntries = 0.0;
            for (auto const& entry : clientEntry.second) {
                if (entry.first > considerStartTime) {
                    cumulatedValidMos += 1.0 + slope * (entry.second - 1.0);
                    numValidEntries += 1.0;
                }
            }

            if (numValidEntries > 0.0) {
                double meanClientMos = cumulatedValidMos / numValidEntries;
                std::pair<std::string, double> mapEntry = std::make_pair(clientName, meanClientMos);
                meanMosPerClient.insert(mapEntry);
            } else if (!clientEntry.second.empty()) {
                std::pair<std::string, double> mapEntry = std::make_pair(clientName, clientEntry.second.back().second);
                meanMosPerClient.insert(mapEntry);
            }
        }
        return meanMosPerClient;
    }

    double linkAdjuster::calculateMeanMosRAClass(std::list<mosListener*> appListeners, simtime_t considerStartTime) {
        double sumMosValues = 0.0;
        double numMosValues = 0.0;
        for (auto const& applicationListener : appListeners) {
            for (auto const& clientNameMosPair : calculateMeanClientMos(applicationListener, considerStartTime)) {
                sumMosValues += clientNameMosPair.second;
                numMosValues += 1.0;
            }
        }
        if (numMosValues > 0.0) {
            return sumMosValues/numMosValues;
        } else {
            return 0.0;
        }
    }

    void linkAdjuster::twoSliceAlgorithm() {
        double connBWSbitrate = getLinkBitrate(getChannelFromName("connBWS").front());
        double connDESbitrate = getLinkBitrate(getChannelFromName("connDES").front());

        double meanMosBWS = calculateMeanMosRAClass(bwsListeners, lastAdjustment);
        emit(meanBWSmosSignal, meanMosBWS);
        double meanMosDES = calculateMeanMosRAClass(desListeners, lastAdjustment);
        emit(meanDESmosSignal, meanMosDES);
        if (meanMosBWS != 0.0 && meanMosDES != 0.0) {
            double mosDifference = meanMosBWS - meanMosDES;
            emit(mosDifferenceSignal, mosDifference);
            if (fabs(mosDifference) > 0.2) {
                connBWSbitrate = std::fmax(10000000, std::fmin(90000000, connBWSbitrate - 2000000*mosDifference));
                connDESbitrate = std::fmax(10000000, std::fmin(90000000, connDESbitrate + 2000000*mosDifference));
            }
        }

        setLinkBitrateByLinkName("connBWS", connBWSbitrate);
        setLinkBitrateByLinkName("connDES", connDESbitrate);
        emit(setBWSbitrateSignal, getLinkBitrate(getChannelFromName("connBWS").front()));
        emit(setDESbitrateSignal, getLinkBitrate(getChannelFromName("connDES").front()));
        return;
    }


    void linkAdjuster::handleMessage(cMessage *msg) {
        EV << msg->getKind() << endl;
        switch (msg->getKind()) {
            case MSGKIND_ADJUSTRATE: {
                if (connChannels.size() > 0) {
                    twoSliceAlgorithm();
                    lastAdjustment = simTime();
//                    setLinkBitrateByLinkName("connFIX", getLinkBitrate(getChannelFromName("connFIX").front())*1.1);
                }
                timeoutMsg->setKind(MSGKIND_ADJUSTRATE);
                scheduleAt(simTime() + adjustmentInterval, timeoutMsg);
                break;
            }
            default:
                throw cRuntimeError("Invalid timer msg: kind=%d", msg->getKind());
        }

    }

} /* namespace inet */





