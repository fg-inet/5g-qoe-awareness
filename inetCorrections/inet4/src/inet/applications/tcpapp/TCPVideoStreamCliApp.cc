/*
 *  TCPVideoStreamCliApp.cc
 *
 *  1. An adaptation of Navarro Joaquim's code (https://github.com/navarrojoaquin/adaptive-video-tcp-omnet)
 *     created on 8 de dez de 2017 by Anderson Andrei da Silva & Patrick Menani Abrah������������������������������������������������������o at University of S������������������������������������������������������o Paulo
 *
 *  2. Edited and adapted for Omnet++ 5.1 with INET 3.5 by Marcin Bosk at the Technische Universit������t Berlin in January 2019
 *
 */

#include "TCPVideoStreamCliApp.h"
#include "inet/applications/tcpapp/GenericAppMsg_m.h"

#include "inet/common/ModuleAccess.h"
#include "inet/mobility/contract/IMobility.h"

#include "inet/common/lifecycle/ModuleOperations.h"
#include "inet/common/packet/Packet.h"
#include "inet/common/TimeTag_m.h"

#include <random>
#include <string>

namespace inet {

#define MSGKIND_CONNECT     0
#define MSGKIND_SEND        1
#define MSGKIND_VIDEO_PLAY  2

//Register_Class(TCPVideoStreamCliApp);
Define_Module(TCPVideoStreamCliApp);

simsignal_t TCPVideoStreamCliApp::rcvdPkSignal = registerSignal("rcvdPk");
simsignal_t TCPVideoStreamCliApp::sentPkSignal = registerSignal("sentPk");

simsignal_t TCPVideoStreamCliApp::positionX = registerSignal("positionX");
simsignal_t TCPVideoStreamCliApp::positionY = registerSignal("positionY");

TCPVideoStreamCliApp::~TCPVideoStreamCliApp() {
    cancelAndDelete(timeoutMsg);
}

TCPVideoStreamCliApp::TCPVideoStreamCliApp() {
    timeoutMsg = NULL;
}

void TCPVideoStreamCliApp::nextVidSetup() {
    cumulatedReceivedBytes = 0;
    numRequestsToSend = ceil((double)video_duration/(double)segment_length);

    video_buffer = 0;
    emit(DASH_buffer_length_signal, video_buffer);
    std::pair<simtime_t, double> timeBufferPair;
    timeBufferPair.first = simTime();
    timeBufferPair.second = video_buffer;
    bufferLength.push_back(timeBufferPair);

    video_playback_pointer = 0;
    emit(DASH_playback_pointer, video_playback_pointer);
    std::pair<simtime_t, double> timePlaybackPair;
    timePlaybackPair.first = simTime();
    timePlaybackPair.second = video_playback_pointer;
    playbackPointer.push_back(timePlaybackPair);

    video_current_quality_index = 0;
    std::pair<simtime_t, double> timeQualityPair;
    timeQualityPair.first = simTime();
    timeQualityPair.second = video_packet_size_per_second[video_current_quality_index];
    videoBitrate.push_back(timeQualityPair);

    video_is_playing = false;
    received_bytes = 0;

    //statistics
    msgsRcvd = msgsSent = bytesRcvd = bytesSent = 0;

    timeoutMsg = new cMessage("timer");
    timeoutMsg->setKind(MSGKIND_CONNECT);

    simtime_t d = simTime() + (simtime_t) par("idleInterval");
    rescheduleOrDeleteTimer(d, MSGKIND_CONNECT);
}

void TCPVideoStreamCliApp::initialize(int stage) {
    TcpBasicClientApp::initialize(stage);
    if (stage != 3)
        return;
    cumulatedReceivedBytes = 0;
    // read Adaptive Video (AV) parameters
    const char *str = par("video_packet_size_per_second").stringValue();
    video_packet_size_per_second = cStringTokenizer(str).asIntVector(); //M:Number of kilobits per second in the video
    video_buffer_max_length = par("video_buffer_max_length"); //M:Maximal length of the video buffer in seconds EDIT? Do it in segments
    video_duration = par("video_duration");                   //M:EDIT? Do that also in segments?
    manifest_size = par("manifest_size");
    segment_length = par("segment_length");
    numRequestsToSend = ceil((double)video_duration/(double)segment_length);
    EV << "Initial numRequestsToSend = " << numRequestsToSend << endl;
    EV << "video_duration % segment_length = " << video_duration % segment_length << endl;

    WATCH(video_buffer);
    video_buffer = 0;
    DASH_buffer_length_signal = registerSignal("DASHBufferLength");
    emit(DASH_buffer_length_signal, video_buffer);
    std::pair<simtime_t, double> timeBufferPair;
    timeBufferPair.first = simTime();
    timeBufferPair.second = video_buffer;
    bufferLength.push_back(timeBufferPair);

    video_playback_pointer = 0;
    WATCH(video_playback_pointer);
    DASH_playback_pointer = registerSignal("DASHVideoPlaybackPointer");
    emit(DASH_playback_pointer, video_playback_pointer);
    std::pair<simtime_t, double> timePlaybackPair;
    timePlaybackPair.first = simTime();
    timePlaybackPair.second = video_playback_pointer;
    playbackPointer.push_back(timePlaybackPair);

    video_current_quality_index = 0;  // start with min quality
    DASH_video_bitrate_signal = registerSignal("DASHVideoBitrate");
    emit(DASH_video_bitrate_signal, video_packet_size_per_second[video_current_quality_index]);
    std::pair<simtime_t, double> timeQualityPair;
    timeQualityPair.first = simTime();
    timeQualityPair.second = video_packet_size_per_second[video_current_quality_index];
    videoBitrate.push_back(timeQualityPair);
    EV << "quality zones: " << video_packet_size_per_second[2] << endl;

    video_is_playing = false;
    received_bytes = 0;
    DASH_video_is_playing_signal = registerSignal("DASHVideoPlaybackStatus");
    DASH_received_bytes = registerSignal("DASHReceivedBytes");
    DASHmosScoreSignal = registerSignal("DASHmosScore");

    //statistics
    msgsRcvd = msgsSent = bytesRcvd = bytesSent = 0;

    WATCH(msgsRcvd);
    WATCH(msgsSent);
    WATCH(bytesRcvd);
    WATCH(bytesSent);

    WATCH(numRequestsToSend);

    timeoutMsg = new cMessage("timer");
    timeoutMsg->setKind(MSGKIND_CONNECT);

    std::string moduleName = getParentModule()->getFullName();
    std::string configName = cSimulation::getActiveEnvir()->getConfigEx()->getActiveConfigName();
    std::string runNumber = std::to_string(cSimulation::getActiveEnvir()->getConfigEx()->getActiveRunNumber());
    nodeIdentifier = configName;
    nodeIdentifier += runNumber;
    nodeIdentifier += moduleName;

    useFlexibleFlag = par("useFlexibleBitrate").stringValue();

    EV << "TCP Video Stream client initialization complete" << endl;
}

void TCPVideoStreamCliApp::sendRequest() {
    EV << "Send request function. ";
    if (video_buffer <= video_buffer_max_length - segment_length) {
        EV<< "Sending request, " << numRequestsToSend-1 << " more to go\n";

        // Request length
        long requestLength = par("requestLength");
        if (requestLength < 1) requestLength = 1;
        // Reply length
        long replyLength = -1;
        if (manifestAlreadySent) {
            // Determine the bitrate of the next segment to download
            int reqVideoBitrate = video_packet_size_per_second[video_current_quality_index]; // kbits -> bytes.
            if (useFlexibleFlag == "flexible") { // Introduce a random offset to the requested video bitrate as in reality the video does not always have the same bitrate in each segment
                cNormal *normal = new cNormal(getRNG(0), reqVideoBitrate, reqVideoBitrate*0.15);
                reqVideoBitrate = normal->draw();
                delete normal;
            }
            // Determine how much data should be requested in order to download the next segment
            if (video_duration % segment_length > 0 && numRequestsToSend == 1) {
                EV << "Download last partial segment" << endl;
                replyLength = (reqVideoBitrate / 8 * 1000) * (video_duration % segment_length);  // Download the partial remaining segment.
            } else {
                EV << "Download whole segment" << endl;
                replyLength = (reqVideoBitrate / 8 * 1000) * segment_length;  // Download the whole segment.
            }

            // Log requested quality
//            emit(DASH_video_bitrate_signal, video_packet_size_per_second[video_current_quality_index]);
            emit(DASH_video_bitrate_signal, reqVideoBitrate);
            std::pair<simtime_t, double> timeQualityPair;
            timeQualityPair.first = simTime();
//            timeQualityPair.second = video_packet_size_per_second[video_current_quality_index];
            timeQualityPair.second = reqVideoBitrate;
            videoBitrate.push_back(timeQualityPair);

            numRequestsToSend--;
            // Switching algoritm
            tLastPacketRequested = simTime();
        } else {
            replyLength = manifest_size;
            EV<< "sending manifest request\n";
        }

        EV << "Requested reply size = " << replyLength << endl;

        msgsSent++;
        bytesSent += requestLength;

        const auto& payload = makeShared<GenericAppMsg>();
        Packet *packet = new Packet("data");
        payload->addTag<CreationTimeTag>()->setCreationTime(simTime());
        payload->setChunkLength(B(requestLength));
        payload->setExpectedReplyLength(B(replyLength));
        payload->setServerClose(false);
        packet->insertAtBack(payload);
        EV << "TCPSocket - sendRequest - connectionId: " << packet->getControlInfo() << endl;
        sendPacket(packet);
        requestedReplyLengths.push_back(replyLength);
    } else {
        EV << "Request will be sent at a later time, as there is not enough space in the buffer." << endl;
        simtime_t d = simTime() + 1;
        rescheduleOrDeleteTimer(d, MSGKIND_SEND);
    }
}

void TCPVideoStreamCliApp::handleTimer(cMessage *msg) {
    EV << "Handling the timer\n";
    std::pair<simtime_t, double> timePlayingPair;
    std::pair<simtime_t, double> timeBufferPair;
    std::pair<simtime_t, double> timePointerPair;

    switch (msg->getKind()) {
    case MSGKIND_CONNECT:       //M:Connect with the server on MSGKIND_CONNECT event
        EV<< "Start the session and connect with the server\n";

        emit(DASH_video_is_playing_signal, video_is_playing);
        timePlayingPair.first = simTime();
        timePlayingPair.second = video_is_playing;
        videoPlaying.push_back(timePlayingPair);

        connect(); // active OPEN
        break;

    case MSGKIND_SEND:          //M:Send a request to the server and ask for some video data on MSGKIND_SEND event
        EV << "Sending a request to the server\n";
        sendRequest();
        // no scheduleAt(): next request will be sent when reply to this one
        // arrives (see socketDataArrived())
        break;

    case MSGKIND_VIDEO_PLAY:    //M:"Play" one second of video on MSGKIND_VIDEO_PLAY event
        EV << "---------------------> Video play event" << endl;
        EV << "Playing one second of video" << endl;
        cancelAndDelete(msg);
        video_buffer -= 1;                                         //M:Take the played part of video (whole segment) out of the buffer

        emit(DASH_buffer_length_signal, video_buffer);
        timeBufferPair.first = simTime();
        timeBufferPair.second = video_buffer;
        bufferLength.push_back(timeBufferPair);

        video_playback_pointer += 1;                               //M:Advance the video pointer (by the whole segment)

        emit(DASH_playback_pointer, video_playback_pointer);
        timePointerPair.first = simTime();
        timePointerPair.second = video_playback_pointer;
        playbackPointer.push_back(timePointerPair);

        if (video_buffer == 0) { //M:"Stop" the video from playing when we played the last segment present in the buffer
            video_is_playing = false;

            emit(DASH_video_is_playing_signal, video_is_playing);
            std::pair<simtime_t, double> timePlayingPair;
            timePlayingPair.first = simTime();
            timePlayingPair.second = video_is_playing;
            videoPlaying.push_back(timePlayingPair);

        }
        if (video_buffer > 0) {//M:When there is something in the buffer, schedule video playing event in one second
            simtime_t d = simTime() + 1; //M: This +1 is used to schedule a video play event in one second
            cMessage *videoPlaybackMsg = new cMessage("playback");
            videoPlaybackMsg->setKind(MSGKIND_VIDEO_PLAY);
            scheduleAt(d, videoPlaybackMsg);
            //rescheduleOrDeleteTimer(d, MSGKIND_VIDEO_PLAY);
        }
        if (!video_is_buffering && numRequestsToSend > 0 && video_buffer <= video_buffer_max_length - segment_length) { //M: Client is still loading segments (buffer not full) and there is still video left to download
            // Now the buffer has some space
            video_is_buffering = true;
            simtime_t d = simTime();
            rescheduleOrDeleteTimer(d, MSGKIND_SEND);
        }
        if (video_buffer == 0 && numRequestsToSend == 0) {    //EDIT! //M: Just a message that the video has been played completely
            EV << "Entire video has been played." << endl;    //EDIT!
            // Calculate MOS here after the whole video has been played
            double mos = calculateMOS();
            EV << "Mean Opinion Score calculated for video. Value = " << mos << "\n";
            emit(DASHmosScoreSignal, mos);
            nextVidSetup();
        }                                                     //EDIT!
        break;
    default:
        EV << "Default case\n";
        throw cRuntimeError("Invalid timer msg: kind=%d", msg->getKind());
    }
}

void TCPVideoStreamCliApp::socketEstablished(TcpSocket *socket) { //M: When the socked has been established, send the first request
    EV << "Socket established\n";                           //EDIT!
    EV << "Connection id: " << socket->getSocketId() << "\n";              //EDIT!
    TcpAppBase::socketEstablished(socket);             //EDIT!

    // perform first request
    sendRequest();

}

void TCPVideoStreamCliApp::rescheduleOrDeleteTimer(simtime_t d, short int msgKind) { //M: Not entirely sure how to describe what is happening here. It probably has something to do with the lifetime of the video client in the simulation
    EV << "Reschedule or delete timer\n";                   //EDIT!
    cancelEvent (timeoutMsg);

    if (stopTime == 0 || stopTime > d) {
        timeoutMsg->setKind(msgKind);
        scheduleAt(d, timeoutMsg);
    } else {
        delete timeoutMsg;
        timeoutMsg = NULL;
    }
}

void TCPVideoStreamCliApp::socketDataArrived(TcpSocket *socket, Packet *msg, bool urgent) {
    int just_received_bytes = msg->getByteLength();
    EV << "Socket data arrived on connection ID: " << socket->getSocketId() << ". Client received " << just_received_bytes << " Bytes\n";
    TcpAppBase::socketDataArrived(socket, msg, urgent);            //EDIT!
    cumulatedReceivedBytes += just_received_bytes;
    long awaitedNumberOfBytes = requestedReplyLengths.front();
    EV << "Accumulated number of received Bytes: " << cumulatedReceivedBytes << "; Number of bytes required: " << awaitedNumberOfBytes << "\n";
    if (cumulatedReceivedBytes == awaitedNumberOfBytes) {
        emit(DASH_received_bytes, cumulatedReceivedBytes);
        std::pair<simtime_t, double> timeRcvdBytesPair;
        timeRcvdBytesPair.first = simTime();
        timeRcvdBytesPair.second = cumulatedReceivedBytes;
        receivedBytes.push_back(timeRcvdBytesPair);
        cumulatedReceivedBytes = 0;
        requestedReplyLengths.pop_front();
        if (!manifestAlreadySent) {
            EV << "Something with manifest\n";
            manifestAlreadySent = true;
            if (timeoutMsg) {
                // Send new request
                simtime_t d = simTime();
                rescheduleOrDeleteTimer(d, MSGKIND_SEND);
            }
            return;
        }
        // Switching algorithm - it limits the shortest time after which a quality change can be made
        packetTimePointer = (packetTimePointer + 1) % packetTimeArrayLength; //That should be ok...
        packetTime[packetTimePointer] = simTime() - tLastPacketRequested;

        int replySeconds = segment_length;

        if (numRequestsToSend == 0 && video_duration % segment_length > 0) {
            replySeconds = video_duration % segment_length;
        }

        EV << "replySeconds = " << replySeconds << endl;

        video_buffer += replySeconds;

        EV << "video_buffer = " << video_buffer << endl;

        emit(DASH_buffer_length_signal, video_buffer);
        std::pair<simtime_t, double> timeBufferPair;
        timeBufferPair.first = simTime();
        timeBufferPair.second = video_buffer;
        bufferLength.push_back(timeBufferPair);

        // Update switch timer
        if(!can_switch) {
            EV << "Switch timer: " << switch_timer << endl;
            switch_timer--;
            if (switch_timer == 0) {
                can_switch = true;
                switch_timer = switch_timeout;
            }
        }
        // Full buffer
        if (video_buffer >= video_buffer_max_length) {  //EDIT!
            EV << "Video buffer full\n";
            video_is_buffering = false;
            // switch to higher quality (if possible)
    //        if (can_switch) {
    //            // Switching algorithm
    //            simtime_t tSum = 0;
    //            for (int i = 0; i < packetTimeArrayLength; i++) {
    //                tSum = tSum + packetTime[i];
    //            }
    //            double estimatedBitRate = (packetTimeArrayLength * video_packet_size_per_second[video_current_quality_index]) / tSum;
    //            EV<< "---------------------> Bit rate estimation:\n";
    //            EV<< "---------------------> Estimated bit rate = " << estimatedBitRate << "\n";
    //            int qmax = video_packet_size_per_second.size() -1;
    //            if (estimatedBitRate > video_packet_size_per_second[std::min(video_current_quality_index + 1, qmax)]) {
    //                video_current_quality_index = std::min(video_current_quality_index + 1, qmax);
    //                can_switch = false;
    //            }
    //        }
            // the next video fragment will be requested when the buffer gets some space, so nothing to do here.
            return;
        }

        // Algorithm to choose the video quality
        int num_qualities = video_packet_size_per_second.size(); // Number of possible quality classes
        int bufLenForLowestQuality = ceil((double)video_buffer_max_length / 4.0);
        int quality_range = (video_buffer_max_length-bufLenForLowestQuality)/(num_qualities - 1); //Range of the quality classes in terms of the place in buffer when the switch occurs

        if (can_switch) {
            if (video_buffer <= bufLenForLowestQuality) {
                video_current_quality_index = 0;
            } else {                                            // Otherwise choose the quality according to the buffer length zone it fits into
                int quality_zone = ceil((double)(video_buffer - bufLenForLowestQuality)/(double)quality_range);
                video_current_quality_index = quality_zone;
            }
            can_switch = false;
        }


        EV<< "---------------------> Buffer=" << video_buffer << "    min= " << video_buffer_min_rebuffering << "\n";           //EDIT!
        // Exit rebuffering state and continue the video playback
        EV << "numRequestsToSend = " << numRequestsToSend << "; video_playback_pointer = " << video_playback_pointer << endl;   //EDIT!

        if ((numRequestsToSend >= 0 && video_buffer >= video_buffer_min_rebuffering) || (numRequestsToSend == 0 && video_playback_pointer < video_duration) ) { //EDIT!
            if (!video_is_playing) {
                EV << "Video is not playing anymore..." << endl;
                video_is_playing = true;

                emit(DASH_video_is_playing_signal, video_is_playing);
                std::pair<simtime_t, double> timePlayingPair;
                timePlayingPair.first = simTime();
                timePlayingPair.second = video_is_playing;
                videoPlaying.push_back(timePlayingPair);

                simtime_t d = simTime() + 1;   //M: This +1 is used to schedule video play event in one second
                cMessage *videoPlaybackMsg = new cMessage("playback");
                videoPlaybackMsg->setKind(MSGKIND_VIDEO_PLAY);
                scheduleAt(d, videoPlaybackMsg);
                //rescheduleOrDeleteTimer(d, MSGKIND_VIDEO_PLAY);
            }
        } else {
            EV << "We are changing the video quality index" << endl;    //EDIT!
            video_current_quality_index = std::max(video_current_quality_index - 1, 0);
        }

        if (numRequestsToSend > 0) {
            EV<< "reply arrived\n";

            if (timeoutMsg)
            {
                // Send new request
                simtime_t d = simTime();
                rescheduleOrDeleteTimer(d, MSGKIND_SEND);
            }
            int recvd = just_received_bytes;
            msgsRcvd++;
            bytesRcvd += recvd;
        }
        else if (socket->getState() == 6)                            //EDIT! //M: There is still a case somewhere that tries to close the socket even though it has been already closed.
        {                                                           //EDIT! //M: That's the reason for this if...
            EV << "Session seems to be closed already" << endl;     //EDIT!
        }                                                           //EDIT!
        else //M: Only close if the socket is not closed already!
        {
            EV << "reply to last request arrived, closing session\n";
            close();
        }
    }
}

// Prepare CSV with the information required for MOS calculation
void TCPVideoStreamCliApp::prepareCSV(void) {
    std::fstream fout;
    std::string filename ("videoMOScalcFiles/tempCSV/");
    filename += nodeIdentifier;
    filename += ".csv";
    EV << "File to open: " << filename << "\n";
    fout.open(filename, std::ios::out | std::ios::trunc);
    fout << "DASHBufferLengthTS,DASHBufferLengthValues," <<
            "DASHReceivedBytesTS,DASHReceivedBytesValues," <<
            "DASHVideoBitrateTS,DASHVideoBitrateValues," <<
            "DASHVideoPlaybackPointerTS,DASHVideoPlaybackPointerValues," <<
            "DASHVideoPlaybackStatusTS,DASHVideoPlaybackStatusValues\n";

    int vblSize = bufferLength.size();
    int rbSize = receivedBytes.size();
    int vbrSize = videoBitrate.size();
    int vppSize = playbackPointer.size();
    int vpsSize = videoPlaying.size();

    int maxSize = 0;
    if (vblSize > maxSize) maxSize = vblSize;
    if (rbSize > maxSize) maxSize = rbSize;
    if (vbrSize > maxSize) maxSize = vbrSize;
    if (vppSize > maxSize) maxSize = vppSize;
    if (vpsSize > maxSize) maxSize = vpsSize;

    // Prepare the csv line by line...
    for (int i = 0; i < maxSize; i++) {
        // Start with the buffer length values
        if (!bufferLength.empty()) {
            std::pair<simtime_t, double> blPair;
            blPair = bufferLength.front();
            double precision = (double) blPair.first.getScaleExp();
            double timestamp = (double) blPair.first.raw() * pow(10, precision);
            fout << std::to_string(timestamp) <<
                    "," <<
                    std::to_string(blPair.second) <<
                    ",";
            bufferLength.pop_front();
        } else {
            fout << ",,";
        }
        // Then reveived bytes values
        if (!receivedBytes.empty()) {
            std::pair<simtime_t, double> rbPair;
            rbPair = receivedBytes.front();
            double precision = (double) rbPair.first.getScaleExp();
            double timestamp = (double) rbPair.first.raw() * pow(10, precision);
            fout << std::to_string(timestamp) <<
                    "," <<
                    std::to_string(rbPair.second) <<
                    ",";
            receivedBytes.pop_front();
        } else {
            fout << ",,";
        }
        // Then video bitrate values
        if (!videoBitrate.empty()) {
            std::pair<simtime_t, double> vbPair;
            vbPair = videoBitrate.front();
            double precision = (double) vbPair.first.getScaleExp();
            double timestamp = (double) vbPair.first.raw() * pow(10, precision);
            fout << std::to_string(timestamp) <<
                    "," <<
                    std::to_string(vbPair.second) <<
                    ",";
            videoBitrate.pop_front();
        } else {
            fout << ",,";
        }
        // Then playback pointer values
        if (!playbackPointer.empty()) {
            std::pair<simtime_t, double> ppPair;
            ppPair = playbackPointer.front();
            double precision = (double) ppPair.first.getScaleExp();
            double timestamp = (double) ppPair.first.raw() * pow(10, precision);
            fout << std::to_string(timestamp) <<
                    "," <<
                    std::to_string(ppPair.second) <<
                    ",";
            playbackPointer.pop_front();
        } else {
            fout << ",,";
        }
        // Then playback status values
        if (!videoPlaying.empty()) {
            std::pair<simtime_t, bool> psPair;
            psPair = videoPlaying.front();
            double precision = (double) psPair.first.getScaleExp();
            double timestamp = (double) psPair.first.raw() * pow(10, precision);
            fout << std::to_string(timestamp) <<
                    "," <<
                    std::to_string((double) psPair.second) <<
                    "\n";
            videoPlaying.pop_front();
        } else {
            fout << ",\n";
        }
    }

    fout.close();
}



double TCPVideoStreamCliApp::calculateMOS(void) {
    // Prepare csv file used for MOS calculation
    TCPVideoStreamCliApp::prepareCSV(); // Will prepare a csv file with the collected information

    // Prepare JSON file with necessary information for MOS calculation
    // Calls a python script that prepares the JSON that then can by utilized by another python script to calculate the MOS value
    std::string command = "python3 videoMOScalcFiles/code/csvToJson.py ";
    std::string input_file = "videoMOScalcFiles/tempCSV/";
    input_file += nodeIdentifier;
    input_file += ".csv";
    std::string output_file = "videoMOScalcFiles/tempJSON/";
    output_file += nodeIdentifier;
    output_file += ".json";
    command += input_file;
    command += " ";
    command += output_file;
    command += " ";
    command += nodeIdentifier;
    std::system(command.c_str());

    // Calculate the MOS value
    // Calls a python script that calculates the MOS value and saves it in a text file
    std::string command2 = "python3 videoMOScalcFiles/code/calcQoE.py ";
    command2 += output_file;
    command2 += " ";
    command2 += nodeIdentifier;
    command2 += " videoMOScalcFiles/tempMOS/";
    command2 += nodeIdentifier;
    command2 += "MOS.txt";
    std::system(command2.c_str());
    std::remove(input_file.c_str());
    std::remove(output_file.c_str());

    // Fetch the MOS value from the text file where it has just been saved
    std::fstream fin;
    std::string filename ("videoMOScalcFiles/tempMOS/");
    filename += nodeIdentifier;
    filename += "MOS.txt";
    EV << "File to open: " << filename << "\n";
    fin.open(filename, std::ios::in);
    double mosValue = 1;
    std::string value;
    if (fin.is_open()) {
        if (getline(fin, value)) {
            mosValue = std::stod(value);
        }
    }
    fin.close();
    std::remove(filename.c_str());
    return mosValue;
}

void TCPVideoStreamCliApp::socketClosed(TcpSocket *socket) {
    EV << "Socket closed. Connection id: " << socket->getSocketId() << "\n";   //EDIT!
    TcpAppBase::socketClosed(socket);                      //EDIT!
}

void TCPVideoStreamCliApp::socketFailure(TcpSocket *socket, int code) {
    EV << "Socket failure. Connection id: " << socket->getSocketId() << "\n";  //EDIT!
//    TCPBasicClientApp::socketFailure(connId, ptr, code);      //EDIT!
    TcpAppBase::socketFailure(socket, code);               //EDIT!

    // reconnect after a delay
    if (timeoutMsg) {
        simtime_t d = simTime() + (simtime_t) par("reconnectInterval");
        rescheduleOrDeleteTimer(d, MSGKIND_CONNECT);
    }
}

void TCPVideoStreamCliApp::refreshDisplay() const
{
    char buf[64];
    sprintf(buf, "rcvd: %ld pks %ld bytes\nsent: %ld pks %ld bytes", msgsRcvd, bytesRcvd, msgsSent, bytesSent);
    getDisplayString().setTagArg("t", 0, buf);
}

}


