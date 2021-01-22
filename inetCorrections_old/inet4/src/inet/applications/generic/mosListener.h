/*
 * mosListener.h
 *
 *  Created on: Jan 20, 2020
 *      Author: marcin
 */

#ifndef INET_APPLICATIONS_TCPAPP_MOSLISTENER_H_
#define INET_APPLICATIONS_TCPAPP_MOSLISTENER_H_

#include <omnetpp.h>

#include "inet/common/lifecycle/LifecycleOperation.h"

#include <list>

namespace inet {

    class INET_API mosListener : public cListener {
        public:
            mosListener();
            virtual ~mosListener();

            std::map<std::string, std::list<std::pair<simtime_t, double>>> allMos;

            virtual void receiveSignal(cComponent *source, simsignal_t signalID, double t, cObject *details) override;

//            std::map<std::string, std::list<std::pair<simtime_t, double>>> getAllMosValues(void);
//        protected:

    };

}
#endif /* INET_APPLICATIONS_TCPAPP_MOSLISTENER_H_ */
