#!/bin/bash


# ./runSimCampaign.sh -i baselineTest.ini -c baselineTest -t 1 
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sli_LVD-BWS -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle_LVD-BWS -t 1 
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle2sli_LVD-BWS -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliDouble_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliDouble_LVD-BWS -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_5sli -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_5sliSingle -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_5sliSingle5sli -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_5sliDouble -t 1

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_SingleDW_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_SingleDW_LVD-BWS -t 1 

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDW_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDW_LVD-BWS -t 1

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueueDES2_2sliSingle2sli_LVD-BWS -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWR2_LVD-BWS -t 1

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_SingleDWRLQ_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_SingleDWRLQ_LVD-BWS -t 1 
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sli_LVD-BWS -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNS.ini -c baselineTestNS_2sliSingle2sli_LVD-BWS -t 1 

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueueDES4_2sliSingle2sli_LVD-BWS -t 1 

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWRLQ_LVD-BWS -t 1

# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-DES -t 1 &
# ./runSimCampaign.sh -i baselineTestNSPrioQueue.ini -c baselineTestNSPrioQueue_2sliSingle2sliDWRLQPD_LVD-BWS -t 1


# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppStressTest_SSH -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppStressTest_VoIP -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppStressTest_FileDownload2-5MB -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppStressTest_VideoV2 -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppStressTest_NewLiveVideoClient -t 2 

# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppLSTest_SSH -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppLSTest_VoIP -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppLSTest_FileDownload2-5MB -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppLSTest_Video -t 2 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c singleAppLSTest_NewLiveVideoClient -t 2 

# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_5sli_AlgoTest3 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_2sli_LVD-DES_AlgoTest3 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_2sli_LVD-BWS_AlgoTest3 -t 1 


# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_VideoFine -t 3 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_LiveVideoFine -t 3 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_FileDownloadFine -t 3

# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_LiveVideoFineShort -t 5 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_LiveVideoFineLong -t 5

# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_LiveVideoShort -t 5 &
# ./runSimCampaign.sh -i baselineTestV3.ini -c heatMapTest_LiveVideoLong -t 5

# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_fairness_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH100VIP20VID75LVD5FDO50_sSSH1sVIP12sVID51sLVD6sFDO30_fairness_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH100VIP20VID50LVD5FDO75_sSSH4sVIP12sVID35sLVD6sFDO43_min_max -t 1 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH100VIP50VID20LVD5FDO75_sSSH1sVIP29sVID15sLVD6sFDO49_min_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH100VIP75VID20LVD5FDO50_sSSH3sVIP44sVID14sLVD2sFDO37_mean_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH100VIP75VID50LVD5FDO20_sSSH2sVIP44sVID34sLVD6sFDO14_mean_max -t 1 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH100VIP75VID50LVD5FDO20_sSSH1sVIP44sVID34sLVD6sFDO15_mean_max -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH50VIP75VID100LVD5FDO20_sSSH7sVIP45sVID20sLVD7sFDO21_fairness_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_fairness_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH50VIP100VID5LVD20FDO75_sSSH1sVIP36sVID20sLVD20sFDO23_fairness_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH5VIP75VID100LVD20FDO50_sSSH1sVIP44sVID48sLVD6sFDO1_min_min -t 1 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH20VIP100VID75LVD5FDO50_sSSH1sVIP58sVID37sLVD3sFDO1_min_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH5VIP50VID75LVD100FDO20_sSSH18sVIP28sVID29sLVD22sFDO3_min_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_0alpha_SSH5VIP100VID50LVD75FDO20_sSSH1sVIP1sVID50sLVD22sFDO26_mean_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_5alpha_SSH5VIP100VID75LVD20FDO50_sSSH25sVIP26sVID32sLVD6sFDO11_mean_min -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_5sli_10alpha_SSH5VIP75VID50LVD100FDO20_sSSH15sVIP42sVID18sLVD22sFDO3_mean_min -t 1 

# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH100VIP75VID20LVD5FDO50 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH100VIP20VID75LVD5FDO50 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH50VIP75VID100LVD5FDO20 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH20VIP100VID75LVD5FDO50 -t 1
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH50VIP100VID5LVD20FDO75 -t 1 & 
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH100VIP20VID50LVD5FDO75 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH100VIP50VID20LVD5FDO75 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH5VIP75VID100LVD20FDO50 -t 1
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH5VIP50VID75LVD100FDO20 -t 1 & 
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH100VIP75VID50LVD5FDO20 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH5VIP100VID50LVD75FDO20 -t 1 &
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH5VIP100VID75LVD20FDO50 -t 1
# ./runSimCampaign.sh -i baselineTest.ini -c baselineTestVCD_SSH5VIP75VID50LVD100FDO20 -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP20VID75LVD5FDO50_sDES14sBWS86_ndf_ndf -t 1
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH50VIP75VID100LVD5FDO20_sDES46sBWS54_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH50VIP100VID5LVD20FDO75_sDES59sBWS41_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP20VID50LVD5FDO75_sDES15sBWS85_ndf_ndf -t 1
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP50VID20LVD5FDO75_sDES31sBWS69_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP75VID100LVD20FDO50_sDES47sBWS53_ndf_ndf -t 1 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP50VID75LVD100FDO20_sDES18sBWS82_ndf_ndf -t 1 & 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH100VIP75VID50LVD5FDO20_sDES46sBWS54_ndf_ndf -t 1 
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH5VIP100VID50LVD75FDO20_sDES60sBWS40_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH5VIP100VID75LVD20FDO50_sDES57sBWS43_ndf_ndf -t 1 &
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_10alpha_SSH5VIP75VID50LVD100FDO20_sDES43sBWS57_ndf_ndf -t 1

# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_5alpha_SSH20VIP100VID75LVD5FDO50_sDES58sBWS42_ndf_ndf -t 1
# ./runSimCampaign.sh -i optimizationAlgoTest.ini -c optimizationAlgoFairness1_2sli_LVD-BWS_0alpha_SSH100VIP75VID20LVD5FDO50_sDES46sBWS54_ndf_ndf -t 1 &


# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_5sli_AlgoTest_alpha00 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_5sli_AlgoTest_alpha05 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_5sli_AlgoTest_alpha10 -t 1 

# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha00 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha05 -t 1 &
# ./runSimCampaign.sh -i baselineTestNSAlgo.ini -c baselineTestNS_2sli_LVD-BWS_AlgoTest_alpha10 -t 1 