/*
 * mosListener.cc
 *
 *  Created on: Jan 20, 2020
 *      Author: marcin
 */


#include "mosListener.h"

namespace inet {

    mosListener::mosListener() {
        EV << "mosListener: Initializing MOS listener\n";
    }

    mosListener::~mosListener() {

    }

    void mosListener::receiveSignal(cComponent *source, simsignal_t signalID, double t, cObject *details) {
        std::string modulePath = source->getFullPath();
        std::string token = modulePath.substr(modulePath.find(".")+1, modulePath.length());
        std::string moduleName = token.substr(0, token.find("."));

        EV << "mosListener: Received MOS = " << t << "\n";
        EV << "mosListener: Details = " << details << "\n";
        EV << "mosListener: Source module = " << moduleName << "\n";
        EV << "mosListener: Signal ID = " << signalID << "\n";

        std::pair<simtime_t, double> timeMosPair = std::make_pair(simTime(), t);

        auto nodeItr = allMos.find(moduleName);
        if (nodeItr == allMos.end()) {
            std::list<std::pair<simtime_t, double>> timeMosList;
            std::pair<std::string, std::list<std::pair<simtime_t, double>>> listEntry = std::make_pair(moduleName, timeMosList);
            allMos.insert(listEntry);
        }
        nodeItr = allMos.find(moduleName);
        nodeItr->second.push_back(timeMosPair);
//        for (auto const& i: nodeItr->second) {
//            EV << "mosListener: List element = " << i.first << ", " << i.second << "\n";
//        }
        return;
    }

//    std::map<std::string, std::list<std::pair<simtime_t, double>>> getAllMosValues(void) {
//        return allMos;
//    }

}
