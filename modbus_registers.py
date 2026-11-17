# -*- coding: utf-8 -*-
"""
Modbus Register Database & Query Engine for RMS IoT SCADA Controllers.
Contains the complete register definitions and helper search/query functions.
"""

RAW_DEFINES_TEXT = """
#define BL_AUTO 2513
#define LAST_BL_COUNTER1 2515
#define LAST_BL_COUNTER2 2517
#define MAX_BILL_RETRIES 2519
#define CURR_BILL_RETRY 2521
#define BILL_UPLOAD 2523
#define LS_TOD_AUTO 2525
#define LAST_TOD_EPOCH1 2527
#define LAST_TOD_EPOCH2 2529
#define MAX_TOD_RETRIES 2531
#define CURR_TOD_RETRY 2533
#define LS_TOD_UPLOAD 2535
#define LS_AUTO 2537
#define LAST_LS_EPOCH1 2539
#define LAST_LS_EPOCH2 2541
#define MAX_LS_RETRIES 2543
#define CURR_LS_RETRY 2545
#define LOAD_UPLOAD 2547
#define LS_DAYS 2549
#define LAST_PRE_SLOT 2551
#define TR_AUTO 2553
#define LAST_TR_EPOCH 2555
#define MAX_TR_RETRIES 2557
#define CURR_TR_RETRY 2559
#define LAST_VOLTAGE_TAMPER_EPOCH1 2561
#define LAST_CURRENT_TAMPER_EPOCH1 2563
#define LAST_POWER_EVENT_EPOCH1 2565
#define LAST_OTHER_TAMPER_EPOCH1 2567
#define LAST_TRXN_TAMPER_EPOCH1 2569
#define LAST_NRLOVER_TAMPER_EPOCH1 2571
#define LAST_VOLTAGE_TAMPER_EPOCH2 2573
#define LAST_CURRENT_TAMPER_EPOCH2 2575
#define LAST_POWER_EVENT_EPOCH2 2577
#define LAST_OTHER_TAMPER_EPOCH2 2579
#define LAST_TRXN_TAMPER_EPOCH2 2581
#define LAST_NRLOVER_TAMPER_EPOCH2 2583
#define TAMPER_UPLOAD 2585
#define LAST_LS_EPOCH3 2587
#define LAST_TOD_EPOCH3 2589
#define LAST_VOLTAGE_TAMPER_EPOCH3 2591
#define LAST_CURRENT_TAMPER_EPOCH3 2593
#define LAST_POWER_EVENT_EPOCH3 2595
#define LAST_OTHER_TAMPER_EPOCH3 2597
#define LAST_TRXN_TAMPER_EPOCH3 2599
#define LAST_NRLOVER_TAMPER_EPOCH3 2601
#define LAST_BL_COUNTER3 2603
#define NET_METER 2605
#define GEN_METER 2607
#define PUMP_METER 2609
#define DLMS_MANUAL_MODE 2611
#define DLMS_METER_TIMEOUT_TIME 2613
#define DLMS_DELAY 2615
#define METER_SELECTION 2617
#define DLMS_DELAY_2 2619
#define METER_SELECTION_2 2621
#define BILLING_TIME 2623
#define METER_CONNECT_COUNT 2625
#define DLMS_METER_STATUS 2627
#define METER_CONNECT_COUNT_2 2629
#define DLMS_METER_STATUS_2 2631
#define M1ERR 2633
#define M2ERR 2635
#define LAST_S1 2637
#define LAST_S2 2639
#define LT_1060_1 2641
#define LT_1060_2 2643
#define LT_1060_3 2645
#define WRITE_METER_CONFIG 2651
#define STATUS1 2653
#define RESET_BASE_WIFI 2655
#define LS_INTERVAL 2661
#define TR_INTERVAL 2663
#define LAST_VR_TIME1 2669
#define LAST_CR_TIME1 2671
#define LAST_PR_TIME1 2673
#define LAST_OR_TIME1 2675
#define LAST_TXR_TIME1 2677
#define LAST_NRR_TIME1 2679
#define LAST_VR_TIME2 2681
#define LAST_CR_TIME2 2683
#define LAST_TXR_TIME2 2685
#define LAST_PR_TIME2 2687
#define LAST_OR_TIME2 2689
#define LAST_NRR_TIME2 2691
#define FW_DOWNLOAD_PROGRESS 2693
#define FW_TOTAL_PARTS 2695
#define FW_OVER_HTTPS 2697
#define FW_LAST_PART_SIZE 2699
#define TR_ENTRY 2705
#define M1_VOLTAGE_ENTRY 2707
#define M2_VOLTAGE_ENTRY 2709
#define M3_VOLTAGE_ENTRY 2711
#define M1_CURRENT_ENTRY 2713
#define M2_CURRENT_ENTRY 2715
#define M3_CURRENT_ENTRY 2717
#define M1_POWER_ENTRY 2719
#define M2_POWER_ENTRY 2721
#define M3_POWER_ENTRY 2723
#define M1_OTHER_ENTRY 2725
#define M2_OTHER_ENTRY 2727
#define M3_OTHER_ENTRY 2729
#define M1_TRXN_ENTRY 2731
#define M2_TRXN_ENTRY 2733
#define M3_TRXN_ENTRY 2735
#define M1_NRLOVER_ENTRY 2737
#define M2_NRLOVER_ENTRY 2739
#define M3_NRLOVER_ENTRY 2741
#define REMOTE_LS_METER 2743
#define REMOTE_LAST_LS_EPOCH 2745
#define REMOTE_LS_LOAD 2747
#define REMOTE_LS_ERROR_CODE 2749
#define REMOTE_LS_TOD_METER 2751
#define REMOTE_LAST_TOD_EPOCH 2753
#define REMOTE_LS_TOD_LOAD 2755
#define REMOTE_LS_TOD_ERROR_CODE 2757
#define REMOTE_BL_METER 2759
#define REMOTE_BILLING_COUNTER 2761
#define REMOTE_BILLING_LOAD 2763
#define REMOTE_BILLING_ERROR_CODE 2765
#define REMOTE_TR_METER 2767
#define REMOTE_LAST_TAMPER_EPOCH 2769
#define REMOTE_TR_TYPE 2771
#define REMOTE_TAMPER_LOAD 2773
#define REMOTE_TAMPER_ERROR_CODE 2775
#define BL_WAIT_TIME 2777
#define TR_WAIT_TIME 2779
#define LS_WAIT_TIME 2781
#define MN_WAIT_TIME 2783
#define WRITE_NET_METER 2785
#define WRITE_GEN_METER 2787
#define WRITE_PUMP_METER 2789
#define WRITE_DLMS_MODE 2791
#define WRITE_SYS_DF 2793
#define WRITE_DLMS_TM 2795
#define WRITE_DLMS_DELAY 2797
#define WRITE_METER_SELECTION 2799
#define WRITE_DLMS_DELAY_2 2801
#define WRITE_METER_SELECTION_2 2803
#define WRITE_DLMS_DELAY_3 2805
#define WRITE_METER_SELECTION_3 2807
#define WRITE_DLMS_DELAY_4 2809
#define WRITE_METER_SELECTION_4 2811
#define WRITE_WIFI_NAME 2813
#define WRITE_WIFI_PASS 2815
#define WRITE_SAVE_CONFIG 2817
#define STORE_SPIFF_EN 2819
#define SPIFF_WRITE_EN_BIT 2821
#define SPIFF_SET_BIT 2823
#define SET_FILENAME 2825
#define METER_TYPE 2827
#define GRID_SUPPLY_STATUS 2839
#define GRID_SUPPLY_THRESHOLD 2841
#define DAY_FIRST_GRID_SUPPLY_RUNHOURS 2843
#define DAY_GRID_SUPPLY_RUNHOURS 2845
#define TILL_DATE_GRID_SUPPLY_RUNHOURS 2847
#define TILL_DATE_OVERLOAD_RUNHOURS 2849
#define DAY_OVERLOAD_RUNHOURS 2851
#define DAY_FIRST_OVERLOAD_RUNHOURS 2853
#define TILL_DATE_LOWPF_RUNHOURS 2859
#define DAY_LOWPF_RUNHOURS 2861
#define DAY_FIRST_LOWPF_RUNHOURS 2863
#define TILL_DATE_TRIPPING_COUNTER 2865
#define DAY_TRIPPING_COUNTER 2867
#define DAY_FIRST_TRIPPING_COUNTER 2869
#define OVER_LOAD_RUNHOUR_STATUS 2871
#define LOWPF_RUNHOUR_STATUS 2873
#define INV_VD 2877
#define INV_INTERVAL 2879
#define RESTRICTION_HOURS 2881
#define AUTO_MODE 2883
#define SCH_ON_TIME 2885
#define SCH_RUN_HOURS 2887
#define SCH_MODE 2889
#define SCH_DAYS 2891
#define SCH_OFF_TIME 2893
#define OPERATION_MODE 2895
#define DO_ON_STATUS 2897
#define DO_OFF_STATUS 2899
#define RESTRICTION_STATUS 2901
#define AUTO_MODE_STATUS 2903
#define RCNTS 2905
#define YCNTS 2907
#define BCNTS 2909
#define CONTACTOR_FAULT 2911
#define RESTRICTION_ENABLE 2913
#define OVER_VOLTAGE_RUNHOUR_STATUS 2915
#define TILL_DATE_OVERVOLTAGE_RUNHOURS 2917
#define DAY_OVERVOLTAGE_RUNHOURS 2919
#define DAY_FIRST_OVERVOLTAGE_RUNHOURS 2921
#define SOLAR_DAY_CHANGE 2923
#define APP_MODE 2931
#define FW_ID_1 2933
#define FW_VER_1 2935
#define FW_UPDATE_1 2937
#define MASTER_REG_WRITE 2955
#define REG_WRITE_RETRY 2957
#define FW_ID1 2959
#define FW_VER 2961
#define FW_UPDATE 2963
#define DEVICE_ON_ACTION 2967
#define DEVICE_OFF_ACTION 2969
#define OPERATION_CHANGE 2971
#define DEVICE_MODE 2973
#define DEVICE_DIDO 2975
#define DEVICE_STATUS 2977
#define POWER_THRESHOLD 2979
#define DEVICE_C_LIMIT 2981
#define DAY_THREE_PHASE_OUTPUT_RUN_HOURS 2983
#define RUN_HOURS_VALUE_REG 2985
#define RUNSEC 2987
#define DAY_FIRST_RUNHOURS 2989
#define DAY_THREE_PHASE_FEEDER_RUN_HOURS 2991
#define TILL_DATE_THREE_PHASE_RUNHOUR 2993
#define DAY_FIRST_THREE_PHASE_FEEDER_RUN_HOURS 2995
#define R_I_PUMP_THRESHOLD 2997
#define Y_I_PUMP_THRESHOLD 2999
#define B_I_PUMP_THRESHOLD 3001
#define PUMP_STATUS 3003
#define THREE_PHASE_RUNHOUR_STATUS 3005
#define TILL_DATE_PUMPRUNHOUR 3007
#define DAY_PUMP_RUN_HOURS 3009
#define DAY_FIRST_PUMP_RUN_HOURS 3011
#define THREE_PHASE_FEEDBACK 3013
#define RESET_MCU 3015
#define PER_REF 3017
#define INPUT_PHASE_FAULT 3019
#define THREE_PHASE_INPUT_STATUS 3021
#define THREE_PHASE_ON_STATUS 3023
#define THREE_PHASEOFF_SET 3025
#define THREE_PHASE_OFF_STATUS 3027
#define THREE_PHASE_ON 3029
#define THREE_PHASE_ON_DELAY 3031
#define THREE_PHASE_OFF_DELAY 3033
#define THREE_PHASE_START_DELAY 3035
#define THREE_PHASE_FAULT 3037
#define THREE_PHASE_FAULT_SP 3039
#define THREE_PHASE_OUTPUT_COMMAND 3041
#define THREE_PHASE_EVENT 3043
#define R_V_ON_SET 3045
#define Y_V_ON_SET 3047
#define B_V_ON_SET 3049
#define SOLAR 3051
#define PHASE 3053
#define TIME_LIMIT 3055
#define DAY_ON_TIME_SOLAR1 3057
#define SOLAR_TIME_ELASPED 3059
#define THREE_PHASE_START_TIME 3061
#define SINGLE_PHASE_INPUT_STATUS 3063
#define SINGLE_PHASE_ON_STATUS 3065
#define SINGLE_PHASE_OFF_STATUS 3067
#define SINGLE_PHASE_ON 3069
#define SINGLE_PHASE_ON_DELAY 3071
#define SINGLE_PHASE_OFF_DELAY 3073
#define DAY_SINGLE_PHASE_FEEDER_RUN_HOURS 3075
#define DAY_FIRST_SINGLE_PHASE_FEEDER_RUN_HOURS 3077
#define TILL_DATE_SINGLE_PHASE_RUNHOUR 3079
#define SINGLE_PHASE_FAULT 3081
#define SINGLE_PHASE_FAULT_SP 3083
#define OVER_CURRENT_PROTECTION_ENABLE 3085
#define R_I_THRESHLOD 3087
#define Y_I_THRESHLOD 3089
#define B_I_THRESHLOD 3091
#define INTERVAL1 3093
#define INTERVAL2 3095
#define INTERVAL3 3097
#define OVER_CURRENT_1PH_LIMIT 3099
#define OVER_CURRENT_STATUS 3101
#define OVER_CURRENT_FLAG 3103
#define R_PHASE_OVERCURRENT_STATUS 3105
#define R_PHASE_OVERCURRENT_FLAG 3107
#define Y_PHASE_OVERCURRENT_STATUS 3109
#define Y_PHASE_OVERCURRENT_FLAG 3111
#define B_PHASE_OVERCURRENT_STATUS 3113
#define B_PHASE_OVERCURRENT_FLAG 3115
#define R_I_REPEAT_COUNT 3117
#define Y_I_REPEAT_COUNT 3119
#define B_I_REPEAT_COUNT 3121
#define R_I_TRIP_ENABLE 3123
#define Y_I_TRIP_ENABLE 3125
#define B_I_TRIP_ENABLE 3127
#define LOAD_TRIP_STATUS 3129
#define REF_COUNT 3131
#define CUTOFF_VOLTAGE_CHECK 3133
#define R_V_CUTOFF 3135
#define Y_V_CUTOFF 3137
#define B_V_CUTOFF 3139
#define CUTOFF_VOLTAGE_CHECK_PERSIST_COUNT 3141
#define CUTOFF_VOLTAGE_STATUS 3143
#define R_PHASE_CUTOFFVOLTAGE_STATUS 3145
#define Y_PHASE_CUTOFFVOLTAGE_STATUS 3147
#define B_PHASE_CUTOFFVOLTAGE_STATUS 3149
#define OVERVOLTAGE_PROTECTION 3151
#define R_V_THRESHOLD 3153
#define Y_V_THRESHOLD 3155
#define B_V_THRESHOLD 3157
#define OVERVOLTAGE_VOLTAGE_CHECK_PERSIST_COUNT 3159
#define OVERVOLTAGE_STATUS 3161
#define R_PHASE_OVERVOLTAGE_STATUS 3163
#define Y_PHASE_OVERVOLTAGE_STATUS 3165
#define B_PHASE_OVERVOLTAGE_STATUS 3167
#define REMOTE_SAVE 3169
#define R_ENABLE 3171
#define Y_ENABLE 3173
#define B_ENABLE 3175
#define R_VALUE 3177
#define Y_VALUE 3179
#define B_VALUE 3181
#define REMOTE_RUN_HOUR 3183
#define R_EPOCH 3185
#define Y_EPOCH 3187
#define B_EPOCH 3189
#define REMOTE_OFF_EPOCH1 3191
#define REMOTE_OFF_EPOCH2 3193
#define REMOTE_OFF_EPOCH3 3195
#define SINGLE_REMOTE_ENABLE 3197
#define SINGLE_REMOTE_VALUE 3199
#define COM_OVERCURRENT_STATUS 3201
#define REMOTE_OFF_TIME 3203
#define PERC_CURR_THRESHOLD 3205
#define OC_CURR_PHASE 3207
#define SDISSUE 3209
#define SINGLE_PHASE_RUNHOUR_STATUS 3211
#define CF_S 3213
#define WRITE_DELAY 3215
#define CONNECTION 3217
#define BILL_INTERVAL 3221
#define TAMPER_INTERVAL 3223
#define LSR_INTERVAL 3225
#define TOD_INTERVAL 3227
#define PSRAM_OK 3229
#define UNBALANCE_VOLT_ENABLE 3231
#define UNBALANCE_VOLT_THRESHOLD 3233
#define UNBALANCE_VOLT_DELAY 3235
#define UNBALANCE_VOLT_STATUS 3237
#define UNBALANCE_VOLT_SM 3239
#define UNBALANCE_VOLT_TILLDATE_RUNHRS 3241
#define UNBALANCE_VOLT_DAY_RUNHRS 3243
#define UNBALANCE_VOLT_DAY_FIRST_RUNHRS 3245
#define UNBALANCE_CURR_ENABLE 3247
#define UNBALANCE_CURR_THRESHOLD 3249
#define UNBALANCE_CURR_DELAY 3251
#define UNBALANCE_CURR_STATUS 3253
#define UNBALANCE_CURR_SM 3255
#define UNBALANCE_CURR_TILLDATE_RUNHRS 3257
#define UNBALANCE_CURR_DAY_RUNHRS 3259
#define UNBALANCE_CURR_DAY_FIRST_RUNHRS 3261
#define LAST_LS_M1_ERR 3263
#define LAST_LS_M2_ERR 3265
#define LAST_BL_M1_ERR 3269
#define LAST_BL_M2_ERR 3271
#define LAST_MN_M1_ERR 3275
#define LAST_MN_M2_ERR 3277
#define LAST_TR_M1_ERR 3281
#define LAST_TR_M2_ERR 3283
#define R_VOL_SP 3285
#define Y_VOL_SP 3287
#define B_VOL_SP 3289
#define METER_ERROR_INTERVAL 3291
#define SINGLE_EPOCH 3293
#define M_STATUS 3295
#define METER_COM_DELAY 3297
#define QUERY_STATUS 3299
#define RESET_RUN_HOURS 3301
#define LOAD_DEFAULT_CONFIG 3303
#define SSL_GSM 3305
#define SSL_CA 3307
#define SSL_CC 3309
#define SSL_CK 3311
#define FILE_CA 3313
#define FILE_CC 3315
#define FILE_CK 3317
#define FILE_UUID 3319
#define FILE_REQ 3321
#define FILE_DEV 3323
#define FILE_NET 3325
#define LOAD_GPRS_CONFIG 3327
#define THREE_PH_SMS 3329
#define EVENT_SMS_DISABLE 3331
#define FIRMWARE 3333
#define SLAVEID 3335
#define GSM_SYNC 3337
#define TIME_UPDATE 3339
#define POLL_REQ3 3341
#define POLL_ERR3 3343
#define WATCHDOG_RESTART 3345
#define MOD_S 3347
#define SIM_S 3349
#define NET_S 3351
#define RTC_S 3353
#define GPRS_S 3355
#define RSSI_S 3357
#define SD_S 3359
#define PF_S 3361
#define FORCEVD_MANUAL 3363
#define MODEM_RESTART 3365
#define SAVE_CONFIG 3367
#define MASTERMOBILE1 3369
#define MASTERMOBILE2 3371
#define POLL_REQ1 3373
#define POLL_ERR1 3375
#define LAST_DATE 3377
#define LAST_TIME 3379
#define SYS_DF 3381
#define DAY_START_TIME 3383
#define SENDACK 3385
#define L_IP1 3387
#define L_IP2 3389
#define L_IP3 3391
#define L_IP4 3393
#define L_MASK1 3395
#define L_MASK2 3397
#define L_MASK3 3399
#define L_MASK4 3401
#define L_GATE1 3403
#define L_GATE2 3405
#define L_GATE3 3407
#define L_GATE4 3409
#define L_DNS1 3411
#define L_DNS2 3413
#define L_DNS3 3415
#define L_DNS4 3417
#define MODULE 3419
#define IP1 3421
#define IP2 3423
#define IP3 3425
#define IP4 3427
#define PORT 3429
#define FTPPORT 3431
#define EEPROMISSUE 3433
#define TEMP 3435
#define GPRS_CHECK_INTERVAL 3437
#define ERROR1 3439
#define ERROR2 3441
#define ERROR3 3443
#define ERROR4 3445
#define ERROR5 3447
#define ERROR6 3449
#define FILE_DELAY 3451
#define SYS_DIAG_FORCE_VD_ENABLE 3453
#define READDO 3455
#define DOMODE 3457
#define TEMP1 3459
#define ERROR12 3461
#define TMCOMM 3463
#define APN 3465
#define USER 3467
#define PASSWORD 3469
#define UPDATE_INTERVAL 3471
#define HEARTBEAT 3473
#define MOBILE1 3475
#define MOBILE2 3477
#define MOBILE3 3479
#define MOBILE4 3481
#define MOBILE5 3483
#define MOBILE6 3485
#define MOBILE7 3487
#define MOBILE8 3489
#define DEFAULT_OVERRIDE 3491
#define BASE_RTC_UPDATE 3493
#define SD_INIT 3495
#define HTTPSPORT 3497
#define DUMMY_SMS 3501
#define ERASE_EEPROM 3503
#define WR_EEPROM 3505
#define READ_EEPROM 3507
#define COUNT_EEPROM_WRITE 3509
#define FTPDOWN 3511
#define AIOFFSET 3513
#define WRITE_EEPROM3 3515
#define WRITE_EEPROM4 3517
#define QOS_FAILCOUNT 3519
#define MAX_QOS_FAILCOUNT 3521
#define DEVICE_STATUS_INV 3523
#define DEVICE_QOS 3525
#define MAX_INVE 3527
#define MAX_DC_CH 3529
#define DUAL_SIM_AUTO 3531
#define POWER_230_MAIN 3533
#define POWER_24_DC 3535
#define POWER_BATTERY 3537
#define BATTERY_MODE_FLAG 3539
#define MODBUS_ERR 3541
#define MODEM_COMM1 3543
#define METER_ERROR_MAX 3545
#define LOGIC_FLAG 3547
#define SEND_DAILY_MSG 3549
#define REG_FLAG 3551
#define DEV_REG_ACT 3553
#define MSG_ID 3555
#define AES_DISABLE 3557
#define FTP_DOWNLOAD 3559
#define VD_STORAGE_TIME 3561
#define VD_STORAGE_TYPE 3563
#define HEARTBEAT_PUSH 3567
#define LAST_DAY_CHANGE 3565
#define ALARM_PUSH 3569
#define HEARTBEAT_TIME 3571
#define DAY_CHANGE_SIM_ENABLE 3573
#define MCU_GPRS_RESET 3575
#define AUTO_TIME_UPDATE_ENABLE 3577
#define RTC_TIME_SAVE 3579
#define VD_LAST_STORAGE_TIME 3581
#define AI1_ERROR 3583
#define AI2_ERROR 3585
#define AI3_ERROR 3587
#define AI4_ERROR 3589
#define AI5_ERROR 3591
#define AI6_ERROR 3593
#define AI1_MODE 3595
#define AI2_MODE 3597
#define AI3_MODE 3599
#define AI4_MODE 3601
#define AI5_MODE 3603
#define AI6_MODE 3605
#define AI1_RESISTOR 3607
#define AI2_RESISTOR 3609
#define AI3_RESISTOR 3611
#define AI4_RESISTOR 3613
#define AI5_RESISTOR 3615
#define AI6_RESISTOR 3617
#define AI1_ENGG_ZERO 3619
#define AI1_ENGG_SPAN 3621
#define AI2_ENGG_ZERO 3623
#define AI2_ENGG_SPAN 3625
#define AI3_ENGG_ZERO 3627
#define AI3_ENGG_SPAN 3629
#define AI4_ENGG_ZERO 3631
#define AI4_ENGG_SPAN 3633
#define AI5_ENGG_ZERO 3635
#define AI5_ENGG_SPAN 3637
#define AI6_ENGG_ZERO 3639
#define AI6_ENGG_SPAN 3641
#define AI1_ELECTRICAL 3643
#define AI2_ELECTRICAL 3645
#define AI3_ELECTRICAL 3647
#define AI4_ELECTRICAL 3649
#define AI5_ELECTRICAL 3651
#define AI6_ELECTRICAL 3653
#define AI1_ENGG 3655
#define AI2_ENGG 3657
#define AI3_ENGG 3659
#define AI4_ENGG 3661
#define AI5_ENGG 3663
#define AI6_ENGG 3665
#define AI1 3667
#define AI2 3669
#define AI3 3671
#define AI4 3673
#define AI5 3675
#define AI6 3677
#define ERR 3679
#define LOAD_DEFAULT_AI 3681
#define POLL_REQ2 3683
#define POLL_ERR2 3685
#define AI1_MF 3687
#define AI2_MF 3689
#define AI3_MF 3691
#define AI4_MF 3693
#define AI5_MF 3695
#define AI6_MF 3697
#define AI1_OFFSET 3699
#define AI2_OFFSET 3701
#define AI3_OFFSET 3703
#define AI4_OFFSET 3705
#define AI5_OFFSET 3707
#define AI6_OFFSET 3709
#define AI1_RAW 3711
#define AI2_RAW 3713
#define AI3_RAW 3715
#define AI4_RAW 3717
#define AI5_RAW 3719
#define AI6_RAW 3721
#define LOAD_CONFIG 3723
#define CONFIG_STORE_FLASH 3725
#define CONFIG_STORE_SD 3727
#define MODBUS_ERR1 3729
#define MODEM_COMM2 3731
#define LAST_QUERY 3733
#define BASETIME_STATUS 3735
#define AUTO_TIME_UPDATE_INTERVAL 3737
#define RTC_UPDATE_TIME 3739
#define WIFI_IDLE_TIME 3741
#define SMS_COUNT 3743
#define SMS_DAILY_LIMIT 3745
#define SPIFFS_ERASE_SIZE 3747
#define SPIFFS_USED 3749
#define FR_WRITE_STATUS2 3751
#define SIM_SLOT_CHANGE_COUNT 3753
#define MODBUS_ERR2 3755
#define MODEM_COMM3 3757
#define SPIFFS_ERROR 3759
#define EPOCH 3761
#define HIST_VD 3763
#define HIST_DATE 3765
#define HIST_INDEX 3767
#define HIST_LOAD 3769
#define HIST_UPLOAD 3771
#define HIST_MSGID 3773
#define SPIFFS_LIST 3775
#define SPIFFS_READ 3777
#define SPIFFS_RDATE 3779
#define SPIFFS_FORMAT 3781
#define SPIFFS_CONFIG_ERASE 3783
#define FORCEVD_COUNT 3785
#define FORCE_ALL 3787
#define READ_FR_DATA 3789
#define FR_ERROR_CODE 3791
#define SPIFFS_ERASE 3793
#define WIFI_STATUS 3795
#define POWER_ON_MIN 3797
#define FR_WD_RESTART 3799
#define PORT_1 3801
#define HIST_EN 3803
#define HIST_ERR 3805
#define DS1307 3807
#define DS1307_DATE 3809
#define DS1307_TIME 3811
#define DS1307_EPOCH 3813
#define DS1307_RTC_UPDATE 3815
#define ESP1_RTC_UPDATE 3817
#define DELAY_RESPONSE 3819
#define DEFAULT_WIFI_MODE 3821
#define DEFAULT_WIFI_MODE_TEMP 3823
#define SD_TRANSFER_TIME 3825
#define SD_TRANSFER_TIME_STAMP 3827
#define SD_TRANSFER_ERROR 3829
#define SD_FORMAT 3831
#define LAST_POFFCNT 3833
#define LAST_POFFTIME_EPOCH 3835
#define POFFTIMEOUT 3837
#define HIST_LIMIT 3839
#define HIST_SENT 3841
#define DEFAULT_WIFI_MODE_TEMP_EN 3843
#define BAUD_115200 3847
#define DEFAULT_WIFI_MODE_OFF 3849
#define SPIFFS_CORRUPT_CMD 3853
#define SPIFFS_CHECK 3855
#define SPIFFS_CHECK_DELAY 3857
#define EEPROM_ERR_COUNT 3859
#define EEPROM_CHECK_DELAY 3861
#define EEPROM_HEALTHY 3863
#define SD_CHECK 3865
#define SD_CHECK_DELAY 3867
#define SD_HEALTHY 3869
#define SD_ERROR 3871
#define SD_CORRUPT_CMD 3873
#define ENABLE_SE2_OLD 3875
#define WINDBOND_DETECTED 3877
#define SPIFFS_TOTAL_SIZE 3879
#define SPIFFS_SET 3881
#define DEVICE_ONTIME 3883
#define DEBUG_EN 3885
#define MODEM_COMM_TEMP 3887
#define DAY_FIRST_DEVICE_ONTIME 3889
#define DLMS_WAIT 3891
#define MUX_SWITCH_TIMEOUT 3893
#define MUX_SWITCH_NEXT_TIMEOUT 3895
#define GET_IMEI1 3897
#define OTA_UPDATE 3899
#define CMD_EN 3901
#define GPSUPDATE 3903
#define LATITUDE 3905
#define LONGITUDE 3907
#define SECURITY_CHECK 3909
#define CONFIG_ERROR 3913
#define METER_FLAG 3915
#define TEMP_REG 3917
#define UPDATE_BATTERY_TIME 3919
#define LAST_PUBLISH_TIME 3921
#define SMS_MAINS_NOTIFY_INTERVAL 3923
#define BATTERY_INTERVAL 3925
#define SMS_PERIODIC_INTERVAL 3927
#define CONNECT_FLAG 3929
#define GPRS_RESTART_ENABLE 3931
#define LOWPF_STATUS 3933
#define LOWPF_THRESHOLD 3935
#define HEARTBEAT_COUNT 3937
#define COTP1 3939
#define POTP1 3941
#define TASK1_STATUS 3947
#define TASK2_STATUS 3949
#define TASK3_STATUS 3951
#define DAY_CHANGE 3953
#define MOUNT_STATUS 3955
#define COTP 3957
#define POTP 3959
#define MUTEX_STATUS 3961
#define REG_TAG 3963
#define REG_TYPE 3965
#define REG_SLAVEID 3967
#define REG_CODE 3969
#define REG_ADD 3971
#define REG_VAL 3973
#define REG_MODBUS_WRITE 3975
#define REG_MODBUS_WRITE_RETRY 3977
#define MAX_RETRY 3979
#define REG_MODBUS_READ 3981
#define REG_ERR_CODE 3983
#define READ_QUERY 3985
#define RSSI1_S 3987
#define RTC_DATE 3989
#define RTC_TIME 3991
#define RTC_TIME_MILLIS 3993
#define RTC_DATE_U 3995
#define RTC_TIME_U 3997
#define RTC_TIME_MILLIS_U 3999
#define RTC_U 4001
#define BMU_DO_UPDATE_AUTO 4003
#define BMU_DO_DEV_ID 4005
#define BMU_DO_NO 4007
#define BMU_DO_VAL 4009
#define WIFI_TX_POWER 4011
#define MILLIS 4013
#define MANUAL_SWITCH 4015
#define SIM 4017
#define AI1_ACT_VALUE 4029
#define AI2_ACT_VALUE 4031
#define AI3_ACT_VALUE 4033
#define AI4_ACT_VALUE 4035
#define AI5_ACT_VALUE 4037
#define AI6_ACT_VALUE 4039
#define AI_OFFSET_CALCULATION 4041
#define AI_CALIBRATION 4043
#define AI_CHANNEL 4045
#define LOAD_UUID 4047
#define MOD_COMM_ERR 4049
#define SIM_DETECT_ERR 4051
#define NET_REG_ERR 4053
#define START_SEQ_ERR 4055
#define ISP_INTERNET_ERR 4057
#define SERV_CONN_ERR 4059
#define GSM_STAGE 4061
#define GPRS_STAGE 4063
#define MQTT_STAGE 4065
#define RESET_GSM_ERR_PARA 4067
#define RESET_SMS_DAY 4069
#define SIM1_SMS_LIMIT 4071
#define SIM2_SMS_LIMIT 4073
#define SIM1_SMS_COUNT 4075
#define SIM2_SMS_COUNT 4077
#define SMS_ERR 4079
#define UPDATE_BAUD 4081
#define RS485_BAUD 4083
#define RS485OVER232 4085
#define ENABLE_DLMS 4087
#define IOT_SOLUTION 4089
#define ENABLE_WDD 4091
#define ENABLE_SEDM 4093
#define ENABLE_WDD_3PH_ONLY 4095
#define COUNT_UUID 4097
#define COUNT_REQ 4099
#define COUNT_DEV 4101
#define COUNT_NET 4103
#define VD1 4105
#define VD2 4107
#define VD3 4109
#define VD4 4111
#define VD5 4113
#define VD6 4115
#define VD7 4117
#define VD8 4119
#define VD9 4121
#define VD10 4123
#define VD11 4125
#define VD12 4127
#define VD13 4129
#define VD14 4131
#define VD15 4133
#define VD16 4135
#define VD17 4137
#define VD18 4139
#define VD19 4141
#define VD20 4143
#define VD21 4145
#define VD22 4147
#define VD23 4149
#define VD24 4151
#define VD25 4153
#define VD26 4155
#define VD27 4157
#define VD28 4159
#define VD29 4161
#define VD30 4163
#define VD28_1 4165
#define VD_TIME1 4169
#define VD_TIME2 4171
#define VD_TIME3 4173
#define VD_TIME4 4175
#define VD_TIME5 4177
#define VD_TIME6 4179
#define VD_TIME7 4181
#define VD_TIME8 4183
#define VD_TIME9 4185
#define VD_TIME10 4187
#define VD_TIME11 4189
#define VD_TIME12 4191
#define VD_TIME13 4193
#define VD_TIME14 4195
#define VD_TIME15 4197
#define VD_TIME16 4199
#define VD_TIME17 4201
#define VD_TIME18 4203
#define VD_TIME19 4205
#define VD_TIME20 4207
#define VD_TIME21 4209
#define VD_TIME22 4211
#define VD_TIME23 4213
#define VD_TIME24 4215
#define VD_TIME25 4217
#define VD_TIME26 4219
#define VD_TIME27 4221
#define VD_TIME28 4223
#define VD_TIME29 4225
#define VD_TIME30 4227
#define VD1_INTERVAL 4233
#define VD2_INTERVAL 4235
#define VD3_INTERVAL 4237
#define VD4_INTERVAL 4239
#define VD5_INTERVAL 4241
#define VD6_INTERVAL 4243
#define VD7_INTERVAL 4245
#define VD8_INTERVAL 4247
#define VD9_INTERVAL 4249
#define VD10_INTERVAL 4251
#define VD11_INTERVAL 4253
#define VD12_INTERVAL 4255
#define VD13_INTERVAL 4257
#define VD14_INTERVAL 4259
#define VD15_INTERVAL 4261
#define VD16_INTERVAL 4263
#define VD17_INTERVAL 4265
#define VD18_INTERVAL 4267
#define VD19_INTERVAL 4269
#define VD20_INTERVAL 4271
#define VD21_INTERVAL 4273
#define VD22_INTERVAL 4275
#define VD23_INTERVAL 4277
#define VD24_INTERVAL 4279
#define VD25_INTERVAL 4281
#define VD26_INTERVAL 4283
#define VD27_INTERVAL 4285
#define VD28_INTERVAL 4287
#define VD29_INTERVAL 4289
#define VD30_INTERVAL 4291
#define VD28_INTERVAL_1 4293
#define DO_WRITE_INTERVEL 4299
#define VD_CONFIG 4301
#define CERT_1_AVAILABLE 4335
#define CERT_2_AVAILABLE 4337
#define CERT_3_AVAILABLE 4339
#define BROKER_CFG_OK 4341
#define CERT1_1_AVAILABLE 4343
#define CERT1_2_AVAILABLE 4345
#define CERT1_3_AVAILABLE 4347
#define BROKER1_CFG_OK 4349
#define GMT_OFFSET 4419
#define DAYLIGHT_OFFSET 4421
#define WIFIONOFFCHECK 4423
#define ENABLE_SE2 4425
#define TIMEOUT_SE2 4427
#define VD_INDEX_SAVE 4429
#define DHCP_DISABLE 4431
#define DHCP_IP1 4433
#define DHCP_IP2 4435
#define DHCP_IP3 4437
#define DHCP_IP4 4439
#define DHCP_MASK1 4441
#define DHCP_MASK2 4443
#define DHCP_MASK3 4445
#define DHCP_MASK4 4447
#define DHCP_GATE1 4449
#define DHCP_GATE2 4451
#define DHCP_GATE3 4453
#define DHCP_GATE4 4455
#define DHCP_DNS1 4457
#define DHCP_DNS2 4459
#define DHCP_DNS3 4461
#define DHCP_DNS4 4463
#define WIFI_RSSI_S 4465
#define WIFI_S 4467
#define WIFI_CONNECT_COUNT 4469
#define WIFI_CONNECT_TIME 4471
#define BROKER_CONNECT_COUNT 4473
#define BROKER_CONNECT_TIME 4475
#define RESET_ENERGY 4477
#define RESET_GT 4479
#define GPRS_EN 4485
#define TAGPERVD 4487
#define DATA_OPT 4489
#define JSON_SIZE_TO_PUSH 4491
#define DATA_OPT_VD_PUSH 4493
#define DATA_OPT_VD_PUSH_TIME 4495
#define STORAGE_SD 4497
#define SD_ERASE_SIZE 4499
#define ACTIVE_STORAGE 4501
#define BUS1_SLAVE 4503
#define DUMMY_TIMEOUT 4509
#define SAVE_BIT 4511
#define FLASH_SAVE 4513
#define ALLDISTATUS 4515
#define TIME_OUT_MOD 4547
#define APPLYRESET 4549
#define FP_SIZE 4551
#define MASTER_MODE 4965
#define MASTER_ADDRESS 4967
#define MASTER_VALUE 4969
#define MASTER_EXECUTION_CMD 4971
#define GSM_AUTO_BAUD_SET 4973
#define GPRS_STATUS 4979
#define FREE_INT 4985
#define LIFE_MIN 4987
#define DUMMY_VAL 4989
#define TIMEOUT_SE3 5041
#define SEL_UUID 5045
#define PHASE_1 5047
#define PHASE_3 5049
#define REG_MODBUS_WRITE_COUNT 5057
#define DEYE_INV 5059
#define DE_DO 5121
#define DE_DLE 5123
#define AUTO_LOAD_EVENT_CONFIG 5125
#define PROCESS_MAS_STATUS 5129
#define WIFI_STATE 5131
#define DEV_QOS 5133
#define WIFI_MODE 5135
#define DELAY_VD_PUSH 5137
#define RTC_FROM_BASE_AUTOUPDATE_ST 5139
#define RTC_BASE_DATE 5141
#define RTC_BASE_TIME 5143
#define RTC_FROM_BASE_RETRY 5145
#define RTC_FROM_BASE_MAX_RETRY 5147
#define UPDATE_CONFIG 5149
#define CURR_DEV 5151
#define WIFI_STATUS1 5161
#define DAY_CHANGE_REST_EN 5163
#define AUTO_INDEX_LOAD 5165
#define AUTO_INDEX_SET 5167
#define RTC_CLK_EN_32K 5229
#define CONFIG_TIMEOUT 5231
#define CONFIG_RID_1 5233
#define CONFIG_RID_2 5235
#define CONFIG_TOTAL 5237
#define CONFIG_PAGE 5239
#define CONFIG_DATA_READY 5241
#define CONFIG_BIT_WISE 5243
#define CONFIG_FILE_ERASE 5245
#define TIMEOUT_RID 5247
#define CONFIG_READ 5249
#define CONFIG_FILE_READ 5251
#define SE2_REG_DATATYPE_1 5253
#define SE2_REG_SLAVEID_1 5255
#define SE2_REGISTER_ADDRESS_1 5257
#define SE2_REG_VALUE_1 5259
#define SEND_RESPONSE 5261
#define WIFI_CHANGE 5263
#define SE2_REG_DATATYPE 5293
#define SE2_REG_SLAVEID 5295
#define SE2_REGISTER_ADDRESS 5297
#define SE2_WRITE_REGISTER 5299 
#define SE2_READ_REGISTER 5301
#define SE2_REG_VALUE 5303
#define SE2_DATA 5305
#define DUMMY_DEVID 5307
#define SE2_REGISTER_ID 5309
#define REG_DATA_BACKUP 5311
#define REG_DATA_BACKUP_SA 5313
#define REG_DATA_BACKUP_LENGTH 5315
#define TEST_DO 5321
#define CONTEXT_SIM 5323
#define CONTEXT_DIS 5325
#define RET_CONTEXT_DIS 5327
#define MD_RESET 5329
#define METER_EXECUTE_CMD 5331
#define METER_MODE 5335
#define METER_ADDRESS 5337
#define METER_VALUE 5339
#define FLAGC1 5361
#define DELAY_NWREG 5363
#define WIFI_TIME 5365
#define POLL_REQ_TEMP 5367
#define POLL_ERR_TEMP 5369
#define BUS2_ERROR 5371
#define BUS2_ERROR_TOT 5373
#define CONFIG_SAVE_TO_CORE 5375
#define CRC_RESULT 5377
#define CRC_FR_STORE 5379
#define NVS_INIT_DATASTORE 5381
#define ENABLE_BUSID_2 5383
#define ENABLE_SEDM_2 5385
#define ALRM_BIT 5391
#define ALRM_VD 5393
#define ALARM_UUID_VAL 5395
#define FR_STORE 5397
#define ALRM_TM 5399
#define ALRM_TMOUT 5401
#define DO_RETRY 5403
#define DEV_ID 5405
#define JSON_UPDATE 5407
#define LAST_NVS_ERR 5409
#define NVS_ERR_CNT 5411
#define FLAG 5413
#define MODSTATUS 5415
#define GPRS_ACTIVE 5417
#define CONNECT_TRY 5419
#define BROKER_CONNECT 5421
#define DEVICE_REG 5423
#define BATTERY_MODE 5425
#define OTP_EN 5427
#define CERT_RENEW_DATE_1 5431
#define CERT_EXPIRY_DATE_1 5433
#define CERT_1 5435
#define CERT_CNT_1 5437
#define CERT_EPOCH_1 5439
#define CERT_PROCESS_ST_1 5441
#define CERT_C_1 5445
#define CERT_ON_DLY_EPOCH_1 5447
#define CERT_ACK_1 5451
#define HIST_ERR_1 5453
#define HIST_VD_1 5455 
#define HIST_UPDATE_VD_1 5457
#define INFO_TOPIC_1 5499
#define THREAD1 5501
#define THREAD2 5503
#define IIOT_NUM 5639
#define IIOT_NUM_1 5641
#define INFO_TOPIC 5643
#define QOS_EN 5645
#define IS_1_0_ST 5649
#define ASN_31 5651
#define CURRENT_COUNT 5653
#define DATABIT 5655
#define STOPBIT 5657
#define PARITY 5659
#define BAUD 5661
#define NET_SETBIT 5663
#define SMS_ENABLE_COUNT 5665
#define SIM_ENABLE_COUNT 5667
#define SMS_TIME 5669
#define NUMBER1 5671
#define NUMBER2 5673
#define CERT_RENEW_DATE 5677
#define CERT_EXPIRY_DATE 5679
#define CERT 5681
#define CERT_CNT 5683
#define CERT_PROCESS_ST 5685
#define CERT_DELAY 5687
#define CERT_EPOCH 5689
#define CERT_C 5691
#define CERT_ON_DLY_EPOCH 5693
#define CERT_ON_DLY 5695
#define CERT_ACK 5697
#define GPRS_START 5699
#define CID_SET 5701
#define CID_SET_1 5703
#define DEL_CERT 5705
#define SERVER_CONNECTION 5707
#define SSL_CA_1 5709
#define SSL_CC_1 5711
#define SSL_CK_1 5713
#define MQTT_STAGE_C1 5715
#define CONNECT_TRY_C1 5717
#define SERV_CONN_ERR_C1 5719
#define DEV_REG_ACT_C1 5721
#define CONNECTION_C1 5725
#define DEVICE_REG_C1 5727
#define BROKER_CONNECT_C1 5729
#define ERROR1_C1 5731
#define SSL_GSM_C1 5733
#define HEARTBEAT_PUSH_C1 5735
#define HEARTBEAT_TIME_C1 5737
#define BROKER_CONNECT_COUNT_C1 5739
#define BROKER_CONNECT_TIME_C1 5741
#define HIST_LOAD_C1 5743
#define HIST_UPLOAD_C1 5745
#define HIST_VD_C1 5747
#define HIST_DATE_C1 5749
#define HIST_INDEX_C1 5751
#define FLAG_C1 5753
#define BATTERY_MODE_FLAG_C1 5755
#define BATTERY_MODE_C1 5757
#define IOT_SOLUTION_C1 5759
#define LAST_PUBLISH_TIME_C1 5761
#define HIST_UPDATE_VD 5763
#define LAST_HIST_CHECK_TIME 5765
#define LAST_HIST_CHECK_TIME_2 5767
#define LAST_HIST_CHECK 5769
#define SLD_TIMEOUT 5771
#define SLD_CONT_SENDING_DATA 5773
#define SLD_TIMEOUT_STOP_S 5775
#define SLD_TIMEOUT_NEXT_EPOCH 5777
#define SLD_INTERVAL 5779
#define SLD_TIMEOUTFORSTOPSENDINGDATA 5781
#define ENERYGY_PUSH_3 5783
#define ENERYGY_PUSH_4 5785
#define ENERYGY_PUSH_3_1 5787
#define ENERYGY_PUSH_4_1 5789
#define SLD_TIMEOUT_1 5791
#define SLD_CONT_SENDING_DATA_1 5793
#define OFF_REG_ADD 5801
#define OFF_VALUE_BITWISE_CHOOSE 5803
#define OFF_VALUE_BITWISE_STORAGE 5805
#define OFF_INVERTOR_METHOD 5807
#define ON_REG_ADD 5815
#define ON_VALUE_BITWISE_CHOOSE 5817
#define ON_VALUE_BITWISE_STORAGE 5819
#define ON_INVERTOR_METHOD 5821
#define FAULT_REG_ADD 5829
#define FAULT_VALUE_BITWISE_CHOOSE 5831
#define FAULT_VALUE_BITWISE_STORAGE 5833
#define FAULT_INVERTOR_METHOD 5835
#define OTHERS_REG_ADD 5843
#define OTHERS_VALUE_BITWISE_CHOOSE 5845
#define OTHERS_VALUE_BITWISE_STORAGE 5847
#define OTHERS_INVERTOR_METHOD 5849
#define SWITCH_EN_REG 5857
#define SWITCH_EN 5859
#define SWITCH_EN_REG_ADD 5861
#define SWITCH_EN_VALUE_BITWISE_CHOOSE 5863
#define SWITCH_EN_VALUE_BITWISE_STORAGE 5865
#define SWITCH_DIS_REG_ADD 5867
#define SWITCH_DIS_VALUE_BITWISE_CHOOSE 5869
#define SWITCH_DIS_VALUE_BITWISE_STORAGE 5871
#define CONTROL_ON_REG_ADD 5873
#define CONTROL_ON_VALUE_BITWISE_CHOOSE 5875
#define CONTROL_ON_VALUE_BITWISE_STORAGE 5877
#define CONTROL_OFF_REG_ADD 5879
#define CONTROL_OFF_VALUE_BITWISE_CHOOSE 5881
#define CONTROL_OFF_VALUE_BITWISE_STORAGE 5883
#define EMERGENCY_SHUTDOWN_REG_ADD 5885
#define EMERGENCY_SHUTDOWN_VALUE_BITWISE_CHOOSE 5887
#define EMERGENCY_SHUTDOWN_VALUE_BITWISE_STORAGE 5889
#define CLOCK_ERROR_CODE 5801
#define CLOCK_START_ADDRESS 5803
#define REGISTER_ERROR_CODE 5809
#define REGISTER_START_ADDRESS 5811
#define CLOCK_ERROR_CODE_2 5931
#define CLOCK_START_ADDRESS_2 5933
#define REGISTER_ERROR_CODE_2 5939
#define REGISTER_START_ADDRESS_2 5941
#define DATA_ERROR_CODE 6091
#define DATA_ERROR_CODE_2 6093
#define STRING_START_ADDRESS 6141
#define STRING_START_ADDRESS_2 6287
"""

from datetime import datetime
import random

SECTIONS = [
    "1. GPRS_Connection",
    "2. SPIFFS_Storage",
    "3. Restart_Count",
    "4. Solar_Power",
    "5. Meters_DLMS",
    "6. Control_Relays",
    "7. System_RTC",
    "8. All_Registers"
]

def categorize_register(name, addr):
    n = name.upper()
    # 2. SPIFFS & Storage
    if any(k in n for k in ["SPIFF", "SD_", "EEPROM", "STORAGE", "FLASH", "NVS", "SET_FILENAME", "FR_STORE", "FR_WRITE"]):
        return "2. SPIFFS_Storage"
    # 3. Restart, Resets & Watchdog Counters
    elif any(k in n for k in ["RESTART", "RESET", "WATCHDOG", "WD_", "RETRY", "TRIP", "POFFCNT", "SLOT_CHANGE", "APPLYRESET"]):
        return "3. Restart_Count"
    # 1. GPRS & Network Connection
    elif any(k in n for k in ["GPRS", "MODEM", "SIM", "NET_", "NETS", "APN", "PORT", "MODULE", "USER", "PASSWORD", "RSSI", "BROKER", "CID", "SERVER", "MQTT", "GSM", "COMM", "WIFI", "IP1", "IP2", "IP3", "IP4", "L_IP", "L_MASK", "L_GATE", "L_DNS", "DHCP", "SSL", "CERT"]):
        return "1. GPRS_Connection"
    # 4. Solar, Grid & Power
    elif any(k in n for k in ["SOLAR", "GRID", "VOLT", "CURR", "POW", "FREQ", "PHASE", "PUMP", "INV", "INVERTER", "VD28", "UNBALANCE", "R_V", "Y_V", "B_V", "R_I", "Y_I", "B_I", "IS_1_0", "POWER_230", "POWER_24", "POWER_BATTERY"]):
        return "4. Solar_Power"
    # 5. Smart Meters & DLMS
    elif any(k in n for k in ["METER", "DLMS", "BILL", "TAMPER", "LS_TOD", "LS_AUTO", "LOAD_UPLOAD", "BL_AUTO", "BL_"]):
        return "5. Meters_DLMS"
    # 6. Control & Relays
    elif any(k in n for k in ["DO", "READDO", "DOMODE", "DEVICE_ON", "DEVICE_OFF", "SWITCH", "RELAY", "CONTACTOR", "FAULT", "CUTOFF", "CMD"]):
        return "6. Control_Relays"
    # 7. System, RTC & CPU
    else:
        return "7. System_RTC"

DESCRIPTIONS = {
    "GPRS_S": "GPRS Attachment Status (0=Detached, 1=Attached & Active)",
    "MOD_S": "Modem Operational Status (0=Off, 1=Initializing, 2=Ready)",
    "SIM_S": "SIM Card Status (0=Not Detected, 1=Ready/Detected)",
    "NET_S": "Cellular Network Registration Status",
    "RSSI_S": "GSM Signal Strength RSSI (CSQ 0-31, 99=Unknown)",
    "MODULE": "Cellular Modem Hardware Model Identifier",
    "IP1": "Cloud MQTT Server IP Address Octet 1",
    "IP2": "Cloud MQTT Server IP Address Octet 2",
    "IP3": "Cloud MQTT Server IP Address Octet 3",
    "IP4": "Cloud MQTT Server IP Address Octet 4",
    "PORT": "Primary MQTT Broker TLS Port (e.g. 8883)",
    "FTPPORT": "FTP Server Port for OTA Firmware",
    "GPRS_CHECK_INTERVAL": "GPRS Link Verification Interval in Seconds",
    "APN": "Cellular Network Access Point Name (APN)",
    "USER": "Cellular APN Authentication Username",
    "PASSWORD": "Cellular APN Authentication Password",
    "UPDATE_INTERVAL": "Data Telemetry Upload Interval in Seconds",
    "HEARTBEAT": "Heartbeat Keep-Alive Interval in Seconds",
    "GPRS_EN": "GPRS Network Communication Master Enable (1=On)",
    "GPRS_ACTIVE": "GPRS Data Connection Live Flag",
    "GPRS_STATUS": "GPRS Connection Status Bitmask",
    "GPRS_START": "GPRS Engine Start / Reconnect Trigger",
    "MCU_GPRS_RESET": "Hardware MCU Commanded GPRS Modem Reset",
    "MODEM_COMM1": "Modem UART Channel 1 Communication State",
    "MODEM_COMM2": "Modem UART Channel 2 Communication State",
    "MODEM_COMM3": "Modem UART Channel 3 Communication State",
    "DUAL_SIM_AUTO": "Automatic Dual SIM Switching Mode (1=Auto)",
    "SIM": "Active SIM Slot Number (1=SIM1, 2=SIM2)",
    "WIFI_S": "WiFi Station Connection Status (1=Connected)",
    "WIFI_RSSI_S": "WiFi Signal Strength RSSI (dBm)",
    "WIFI_MODE": "WiFi Operating Mode (0=Off, 1=AP, 2=STA)",
    "WIFI_STATUS": "WiFi Connection Health Status",
    "SSL_GSM": "GSM SSL/TLS Protocol Profile Active",
    "BROKER_CONNECT": "MQTT Broker Live Connection Status (1=Connected)",
    "DEVICE_REG": "Device Registration Status on Cloud Platform",
    "FIRMWARE": "Controller Firmware Version Code",
    "SLAVEID": "Modbus Device Slave ID (RS485 Address)",
    "RTC_S": "Real-Time Clock Health Status",
    "RTC_DATE": "Current RTC Calendar Date (DDMMYY)",
    "RTC_TIME": "Current RTC Clock Time (HHMMSS)",
    "TEMP": "Internal Enclosure / MCU Temperature (°C)",
    "GRID_SUPPLY_STATUS": "Grid AC Mains Power Supply Status (1=Present)",
    "INV_VD": "Virtual Device VD Table Index for Inverter",
    "VD28": "Virtual Device 28 Data Block (On-Grid Rooftop Telemetry)",
    "VD28_INTERVAL": "VD28 Telemetry Periodic Upload Interval (s)",
    "POWER_230_MAIN": "230V AC Mains Input Power Present Flag",
    "POWER_BATTERY": "Backup Battery Power Supply Active Flag",
    "BATTERY_MODE_FLAG": "Operating on Battery Backup Power (1=Battery)",
    "NET_METER": "Net Meter Communication ID / Address",
    "GEN_METER": "Solar Generation Meter Communication ID",
    "PUMP_METER": "Solar Water Pump Meter Communication ID",
    "ENABLE_DLMS": "DLMS/COSEM Smart Metering Master Protocol Enable",
    "DEVICE_ON_ACTION": "Remote Device Master ON Command Output",
    "DEVICE_OFF_ACTION": "Remote Device Master OFF Command Output",
    "R_V_ON_SET": "R-Phase Line-to-Neutral Voltage Threshold",
    "Y_V_ON_SET": "Y-Phase Line-to-Neutral Voltage Threshold",
    "B_V_ON_SET": "B-Phase Line-to-Neutral Voltage Threshold",
    "R_I_THRESHLOD": "R-Phase Current Load Limit Threshold (A)",
    "Y_I_THRESHLOD": "Y-Phase Current Load Limit Threshold (A)",
    "B_I_THRESHLOD": "B-Phase Current Load Limit Threshold (A)",
    "MILLIS": "System Running Millisecond Counter",
    "MSG_ID": "MQTT Last Message Packet Sequence ID",
    "LOAD_GPRS_CONFIG": "Command to Reload GPRS & Server Parameters from Flash",
    "REG_MODBUS_READ": "Trigger Direct Modbus Register Read Request",
    "REG_MODBUS_WRITE": "Trigger Direct Modbus Register Write Request",
    "REG_ADD": "Target Modbus Register Address for Direct Read/Write",
    "REG_VAL": "Target Modbus Register Value for Direct Read/Write",
}

def parse_modbus_defines():
    regs = []
    seen = set()
    for line in RAW_DEFINES_TEXT.strip().splitlines():
        line = line.strip()
        if not line.startswith("#define"):
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[2].isdigit():
            name = parts[1]
            raw_addr = int(parts[2])
            # All registers shifted +1 to make them all odd numbers
            addr = raw_addr + 1 if raw_addr % 2 == 0 else raw_addr
            if (addr, name) not in seen:
                seen.add((addr, name))
                category = categorize_register(name, addr)
                desc = DESCRIPTIONS.get(name, f"{category} Parameter: {name.replace('_', ' ').title()}")
                regs.append({
                    "address": addr,
                    "name": name,
                    "category": category,
                    "description": desc,
                    "value": "---",
                    "updated_at": "Never"
                })
    # Sort by address
    regs.sort(key=lambda x: x["address"])
    return regs

ALL_REGISTERS = parse_modbus_defines()

def get_registers_by_section(section_name):
    """Filters registers by one of the defined sections or returns all."""
    if section_name.startswith("8") or "ALL" in section_name.upper():
        return list(ALL_REGISTERS)
    return [r for r in ALL_REGISTERS if r["category"] == section_name]

def get_gprs_registers():
    return [r for r in ALL_REGISTERS if r["category"] == "1. GPRS_Connection"]

def search_registers(query="", section="8. All_Registers"):
    q = query.strip().upper()
    results = []
    for r in ALL_REGISTERS:
        if not section.startswith("8") and "ALL" not in section.upper() and r["category"] != section:
            continue
        if not q:
            results.append(r)
        elif (q in str(r["address"]) or 
              q in r["name"].upper() or 
              q in r["category"].upper() or 
              q in r.get("description", "").upper()):
            results.append(r)
    return results

def search_across_all_sections(query=""):
    """
    Searches across all registers and groups matches by section.
    Returns:
      overall_matches: list of matching register dicts
      section_counts: dict of {section_name: count_of_matches}
    """
    q = query.strip().upper()
    overall = []
    section_counts = {s: 0 for s in SECTIONS if not s.startswith("8")}
    for r in ALL_REGISTERS:
        sec = r.get("category", "")
        if not q:
            overall.append(r)
            if sec in section_counts:
                section_counts[sec] += 1
        else:
            if (q in str(r["address"]) or 
                q in r["name"].upper() or 
                q in r.get("description", "").upper() or
                q in sec.upper()):
                overall.append(r)
                if sec in section_counts:
                    section_counts[sec] += 1
    return overall, section_counts

def build_ondemand_payload(reg_name=None, reg_val=None, cmkey="155521", pmkey="438266", cmd="read", custom_timestamp=None, batch_dict=None):
    """
    Constructs the exact requested JSON ondemand payload:
    Single register:
      {"msgid":"6374196","CMKEY":"155521","PMKEY":"438266","timestamp":"2026-09-07 13:35:32","type":"ondemand","cmd":"read","MODBUS_REG_NAME":VALUE_REG_GIVEN_BY_REG}
    Batch / Multi-register:
      {"msgid":"6374196","CMKEY":"155521","PMKEY":"438266","timestamp":"...","type":"ondemand","cmd":"read","REG1":VAL1,"REG2":VAL2,...}
    """
    msgid = str(random.randint(1000000, 9999999))
    now_ts = custom_timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "msgid": str(msgid),
        "CMKEY": str(cmkey if cmkey else "155521"),
        "PMKEY": str(pmkey if pmkey else "438266"),
        "timestamp": now_ts,
        "type": "ondemand",
        "cmd": str(cmd or "read"),
    }

    if batch_dict and isinstance(batch_dict, dict):
        for k, v in batch_dict.items():
            val = v
            if isinstance(v, str) and v.isdigit():
                val = int(v)
            payload[str(k)] = val
    elif isinstance(reg_name, dict):
        for k, v in reg_name.items():
            val = v
            if isinstance(v, str) and v.isdigit():
                val = int(v)
            payload[str(k)] = val
    else:
        val = reg_val
        if isinstance(reg_val, str) and reg_val.isdigit():
            val = int(reg_val)
        payload[str(reg_name)] = val

    return payload
