# -*- coding: utf-8 -*-
"""
Modbus Register Database & Query Engine for RMS IoT SCADA Controllers.
Contains the complete register definitions and helper search/query functions.
"""

RAW_DEFINES_TEXT = """
#define BL_AUTO 2512
#define LAST_BL_COUNTER1 2514
#define LAST_BL_COUNTER2 2516
#define MAX_BILL_RETRIES 2518
#define CURR_BILL_RETRY 2520
#define BILL_UPLOAD 2522
#define LS_TOD_AUTO 2524
#define LAST_TOD_EPOCH1 2526
#define LAST_TOD_EPOCH2 2528
#define MAX_TOD_RETRIES 2530
#define CURR_TOD_RETRY 2532
#define LS_TOD_UPLOAD 2534
#define LS_AUTO 2536
#define LAST_LS_EPOCH1 2538
#define LAST_LS_EPOCH2 2540
#define MAX_LS_RETRIES 2542
#define CURR_LS_RETRY 2544
#define LOAD_UPLOAD 2546
#define LS_DAYS 2548
#define LAST_PRE_SLOT 2550
#define TR_AUTO 2552
#define LAST_TR_EPOCH 2554
#define MAX_TR_RETRIES 2556
#define CURR_TR_RETRY 2558
#define LAST_VOLTAGE_TAMPER_EPOCH1 2560
#define LAST_CURRENT_TAMPER_EPOCH1 2562
#define LAST_POWER_EVENT_EPOCH1 2564
#define LAST_OTHER_TAMPER_EPOCH1 2566
#define LAST_TRXN_TAMPER_EPOCH1 2568
#define LAST_NRLOVER_TAMPER_EPOCH1 2570
#define LAST_VOLTAGE_TAMPER_EPOCH2 2572
#define LAST_CURRENT_TAMPER_EPOCH2 2574
#define LAST_POWER_EVENT_EPOCH2 2576
#define LAST_OTHER_TAMPER_EPOCH2 2578
#define LAST_TRXN_TAMPER_EPOCH2 2580
#define LAST_NRLOVER_TAMPER_EPOCH2 2582
#define TAMPER_UPLOAD 2584
#define LAST_LS_EPOCH3 2586
#define LAST_TOD_EPOCH3 2588
#define LAST_VOLTAGE_TAMPER_EPOCH3 2590
#define LAST_CURRENT_TAMPER_EPOCH3 2592
#define LAST_POWER_EVENT_EPOCH3 2594
#define LAST_OTHER_TAMPER_EPOCH3 2596
#define LAST_TRXN_TAMPER_EPOCH3 2598
#define LAST_NRLOVER_TAMPER_EPOCH3 2600
#define LAST_BL_COUNTER3 2602
#define NET_METER 2604
#define GEN_METER 2606
#define PUMP_METER 2608
#define DLMS_MANUAL_MODE 2610
#define DLMS_METER_TIMEOUT_TIME 2612
#define DLMS_DELAY 2614
#define METER_SELECTION 2616
#define DLMS_DELAY_2 2618
#define METER_SELECTION_2 2620
#define BILLING_TIME 2622
#define METER_CONNECT_COUNT 2624
#define DLMS_METER_STATUS 2626
#define METER_CONNECT_COUNT_2 2628
#define DLMS_METER_STATUS_2 2630
#define M1ERR 2632
#define M2ERR 2634
#define LAST_S1 2636
#define LAST_S2 2638
#define LT_1060_1 2640
#define LT_1060_2 2642
#define LT_1060_3 2644
#define WRITE_METER_CONFIG 2650
#define STATUS1 2652
#define RESET_BASE_WIFI 2654
#define LS_INTERVAL 2660
#define TR_INTERVAL 2662
#define LAST_VR_TIME1 2668
#define LAST_CR_TIME1 2670
#define LAST_PR_TIME1 2672
#define LAST_OR_TIME1 2674
#define LAST_TXR_TIME1 2676
#define LAST_NRR_TIME1 2678
#define LAST_VR_TIME2 2680
#define LAST_CR_TIME2 2682
#define LAST_TXR_TIME2 2684
#define LAST_PR_TIME2 2686
#define LAST_OR_TIME2 2688
#define LAST_NRR_TIME2 2690
#define FW_DOWNLOAD_PROGRESS 2692
#define FW_TOTAL_PARTS 2694
#define FW_OVER_HTTPS 2696
#define FW_LAST_PART_SIZE 2698
#define TR_ENTRY 2704
#define M1_VOLTAGE_ENTRY 2706
#define M2_VOLTAGE_ENTRY 2708
#define M3_VOLTAGE_ENTRY 2710
#define M1_CURRENT_ENTRY 2712
#define M2_CURRENT_ENTRY 2714
#define M3_CURRENT_ENTRY 2716
#define M1_POWER_ENTRY 2718
#define M2_POWER_ENTRY 2720
#define M3_POWER_ENTRY 2722
#define M1_OTHER_ENTRY 2724
#define M2_OTHER_ENTRY 2726
#define M3_OTHER_ENTRY 2728
#define M1_TRXN_ENTRY 2730
#define M2_TRXN_ENTRY 2732
#define M3_TRXN_ENTRY 2734
#define M1_NRLOVER_ENTRY 2736
#define M2_NRLOVER_ENTRY 2738
#define M3_NRLOVER_ENTRY 2740
#define REMOTE_LS_METER 2742
#define REMOTE_LAST_LS_EPOCH 2744
#define REMOTE_LS_LOAD 2746
#define REMOTE_LS_ERROR_CODE 2748
#define REMOTE_LS_TOD_METER 2750
#define REMOTE_LAST_TOD_EPOCH 2752
#define REMOTE_LS_TOD_LOAD 2754
#define REMOTE_LS_TOD_ERROR_CODE 2756
#define REMOTE_BL_METER 2758
#define REMOTE_BILLING_COUNTER 2760
#define REMOTE_BILLING_LOAD 2762
#define REMOTE_BILLING_ERROR_CODE 2764
#define REMOTE_TR_METER 2766
#define REMOTE_LAST_TAMPER_EPOCH 2768
#define REMOTE_TR_TYPE 2770
#define REMOTE_TAMPER_LOAD 2772
#define REMOTE_TAMPER_ERROR_CODE 2774
#define BL_WAIT_TIME 2776
#define TR_WAIT_TIME 2778
#define LS_WAIT_TIME 2780
#define MN_WAIT_TIME 2782
#define WRITE_NET_METER 2784
#define WRITE_GEN_METER 2786
#define WRITE_PUMP_METER 2788
#define WRITE_DLMS_MODE 2790
#define WRITE_SYS_DF 2792
#define WRITE_DLMS_TM 2794
#define WRITE_DLMS_DELAY 2796
#define WRITE_METER_SELECTION 2798
#define WRITE_DLMS_DELAY_2 2800
#define WRITE_METER_SELECTION_2 2802
#define WRITE_DLMS_DELAY_3 2804
#define WRITE_METER_SELECTION_3 2806
#define WRITE_DLMS_DELAY_4 2808
#define WRITE_METER_SELECTION_4 2810
#define WRITE_WIFI_NAME 2812
#define WRITE_WIFI_PASS 2814
#define WRITE_SAVE_CONFIG 2816
#define STORE_SPIFF_EN 2818
#define SPIFF_WRITE_EN_BIT 2820
#define SPIFF_SET_BIT 2822
#define SET_FILENAME 2824
#define METER_TYPE 2826
#define GRID_SUPPLY_STATUS 2838
#define GRID_SUPPLY_THRESHOLD 2840
#define DAY_FIRST_GRID_SUPPLY_RUNHOURS 2842
#define DAY_GRID_SUPPLY_RUNHOURS 2844
#define TILL_DATE_GRID_SUPPLY_RUNHOURS 2846
#define TILL_DATE_OVERLOAD_RUNHOURS 2848
#define DAY_OVERLOAD_RUNHOURS 2850
#define DAY_FIRST_OVERLOAD_RUNHOURS 2852
#define TILL_DATE_LOWPF_RUNHOURS 2858
#define DAY_LOWPF_RUNHOURS 2860
#define DAY_FIRST_LOWPF_RUNHOURS 2862
#define TILL_DATE_TRIPPING_COUNTER 2864
#define DAY_TRIPPING_COUNTER 2866
#define DAY_FIRST_TRIPPING_COUNTER 2868
#define OVER_LOAD_RUNHOUR_STATUS 2870
#define LOWPF_RUNHOUR_STATUS 2872
#define INV_VD 2876
#define INV_INTERVAL 2878
#define RESTRICTION_HOURS 2880
#define AUTO_MODE 2882
#define SCH_ON_TIME 2884
#define SCH_RUN_HOURS 2886
#define SCH_MODE 2888
#define SCH_DAYS 2890
#define SCH_OFF_TIME 2892
#define OPERATION_MODE 2894
#define DO_ON_STATUS 2896
#define DO_OFF_STATUS 2898
#define RESTRICTION_STATUS 2900
#define AUTO_MODE_STATUS 2902
#define RCNTS 2904
#define YCNTS 2906
#define BCNTS 2908
#define CONTACTOR_FAULT 2910
#define RESTRICTION_ENABLE 2912
#define OVER_VOLTAGE_RUNHOUR_STATUS 2914
#define TILL_DATE_OVERVOLTAGE_RUNHOURS 2916
#define DAY_OVERVOLTAGE_RUNHOURS 2918
#define DAY_FIRST_OVERVOLTAGE_RUNHOURS 2920
#define SOLAR_DAY_CHANGE 2922
#define APP_MODE 2930
#define FW_ID_1 2932
#define FW_VER_1 2934
#define FW_UPDATE_1 2936
#define MASTER_REG_WRITE 2954
#define REG_WRITE_RETRY 2956
#define FW_ID1 2958
#define FW_VER 2960
#define FW_UPDATE 2962
#define DEVICE_ON_ACTION 2966
#define DEVICE_OFF_ACTION 2968
#define OPERATION_CHANGE 2970
#define DEVICE_MODE 2972
#define DEVICE_DIDO 2974
#define DEVICE_STATUS 2976
#define POWER_THRESHOLD 2978
#define DEVICE_C_LIMIT 2980
#define DAY_THREE_PHASE_OUTPUT_RUN_HOURS 2982
#define RUN_HOURS_VALUE_REG 2984
#define RUNSEC 2986
#define DAY_FIRST_RUNHOURS 2988
#define DAY_THREE_PHASE_FEEDER_RUN_HOURS 2990
#define TILL_DATE_THREE_PHASE_RUNHOUR 2992
#define DAY_FIRST_THREE_PHASE_FEEDER_RUN_HOURS 2994
#define R_I_PUMP_THRESHOLD 2996
#define Y_I_PUMP_THRESHOLD 2998
#define B_I_PUMP_THRESHOLD 3000
#define PUMP_STATUS 3002
#define THREE_PHASE_RUNHOUR_STATUS 3004
#define TILL_DATE_PUMPRUNHOUR 3006
#define DAY_PUMP_RUN_HOURS 3008
#define DAY_FIRST_PUMP_RUN_HOURS 3010
#define THREE_PHASE_FEEDBACK 3012
#define RESET_MCU 3014
#define PER_REF 3016
#define INPUT_PHASE_FAULT 3018
#define THREE_PHASE_INPUT_STATUS 3020
#define THREE_PHASE_ON_STATUS 3022
#define THREE_PHASEOFF_SET 3024
#define THREE_PHASE_OFF_STATUS 3026
#define THREE_PHASE_ON 3028
#define THREE_PHASE_ON_DELAY 3030
#define THREE_PHASE_OFF_DELAY 3032
#define THREE_PHASE_START_DELAY 3034
#define THREE_PHASE_FAULT 3036
#define THREE_PHASE_FAULT_SP 3038
#define THREE_PHASE_OUTPUT_COMMAND 3040
#define THREE_PHASE_EVENT 3042
#define R_V_ON_SET 3044
#define Y_V_ON_SET 3046
#define B_V_ON_SET 3048
#define SOLAR 3050
#define PHASE 3052
#define TIME_LIMIT 3054
#define DAY_ON_TIME_SOLAR1 3056
#define SOLAR_TIME_ELASPED 3058
#define THREE_PHASE_START_TIME 3060
#define SINGLE_PHASE_INPUT_STATUS 3062
#define SINGLE_PHASE_ON_STATUS 3064
#define SINGLE_PHASE_OFF_STATUS 3066
#define SINGLE_PHASE_ON 3068
#define SINGLE_PHASE_ON_DELAY 3070
#define SINGLE_PHASE_OFF_DELAY 3072
#define DAY_SINGLE_PHASE_FEEDER_RUN_HOURS 3074
#define DAY_FIRST_SINGLE_PHASE_FEEDER_RUN_HOURS 3076
#define TILL_DATE_SINGLE_PHASE_RUNHOUR 3078
#define SINGLE_PHASE_FAULT 3080
#define SINGLE_PHASE_FAULT_SP 3082
#define OVER_CURRENT_PROTECTION_ENABLE 3084
#define R_I_THRESHLOD 3086
#define Y_I_THRESHLOD 3088
#define B_I_THRESHLOD 3090
#define INTERVAL1 3092
#define INTERVAL2 3094
#define INTERVAL3 3096
#define OVER_CURRENT_1PH_LIMIT 3098
#define OVER_CURRENT_STATUS 3100
#define OVER_CURRENT_FLAG 3102
#define R_PHASE_OVERCURRENT_STATUS 3104
#define R_PHASE_OVERCURRENT_FLAG 3106
#define Y_PHASE_OVERCURRENT_STATUS 3108
#define Y_PHASE_OVERCURRENT_FLAG 3110
#define B_PHASE_OVERCURRENT_STATUS 3112
#define B_PHASE_OVERCURRENT_FLAG 3114
#define R_I_REPEAT_COUNT 3116
#define Y_I_REPEAT_COUNT 3118
#define B_I_REPEAT_COUNT 3120
#define R_I_TRIP_ENABLE 3122
#define Y_I_TRIP_ENABLE 3124
#define B_I_TRIP_ENABLE 3126
#define LOAD_TRIP_STATUS 3128
#define REF_COUNT 3130
#define CUTOFF_VOLTAGE_CHECK 3132
#define R_V_CUTOFF 3134
#define Y_V_CUTOFF 3136
#define B_V_CUTOFF 3138
#define CUTOFF_VOLTAGE_CHECK_PERSIST_COUNT 3140
#define CUTOFF_VOLTAGE_STATUS 3142
#define R_PHASE_CUTOFFVOLTAGE_STATUS 3144
#define Y_PHASE_CUTOFFVOLTAGE_STATUS 3146
#define B_PHASE_CUTOFFVOLTAGE_STATUS 3148
#define OVERVOLTAGE_PROTECTION 3150
#define R_V_THRESHOLD 3152
#define Y_V_THRESHOLD 3154
#define B_V_THRESHOLD 3156
#define OVERVOLTAGE_VOLTAGE_CHECK_PERSIST_COUNT 3158
#define OVERVOLTAGE_STATUS 3160
#define R_PHASE_OVERVOLTAGE_STATUS 3162
#define Y_PHASE_OVERVOLTAGE_STATUS 3164
#define B_PHASE_OVERVOLTAGE_STATUS 3166
#define REMOTE_SAVE 3168
#define R_ENABLE 3170
#define Y_ENABLE 3172
#define B_ENABLE 3174
#define R_VALUE 3176
#define Y_VALUE 3178
#define B_VALUE 3180
#define REMOTE_RUN_HOUR 3182
#define R_EPOCH 3184
#define Y_EPOCH 3186
#define B_EPOCH 3188
#define REMOTE_OFF_EPOCH1 3190
#define REMOTE_OFF_EPOCH2 3192
#define REMOTE_OFF_EPOCH3 3194
#define SINGLE_REMOTE_ENABLE 3196
#define SINGLE_REMOTE_VALUE 3198
#define COM_OVERCURRENT_STATUS 3200
#define REMOTE_OFF_TIME 3202
#define PERC_CURR_THRESHOLD 3204
#define OC_CURR_PHASE 3206
#define SDISSUE 3208
#define SINGLE_PHASE_RUNHOUR_STATUS 3210
#define CF_S 3212
#define WRITE_DELAY 3214
#define CONNECTION 3216
#define BILL_INTERVAL 3220
#define TAMPER_INTERVAL 3222
#define LSR_INTERVAL 3224
#define TOD_INTERVAL 3226
#define PSRAM_OK 3228
#define UNBALANCE_VOLT_ENABLE 3230
#define UNBALANCE_VOLT_THRESHOLD 3232
#define UNBALANCE_VOLT_DELAY 3234
#define UNBALANCE_VOLT_STATUS 3236
#define UNBALANCE_VOLT_SM 3238
#define UNBALANCE_VOLT_TILLDATE_RUNHRS 3240
#define UNBALANCE_VOLT_DAY_RUNHRS 3242
#define UNBALANCE_VOLT_DAY_FIRST_RUNHRS 3244
#define UNBALANCE_CURR_ENABLE 3246
#define UNBALANCE_CURR_THRESHOLD 3248
#define UNBALANCE_CURR_DELAY 3250
#define UNBALANCE_CURR_STATUS 3252
#define UNBALANCE_CURR_SM 3254
#define UNBALANCE_CURR_TILLDATE_RUNHRS 3256
#define UNBALANCE_CURR_DAY_RUNHRS 3258
#define UNBALANCE_CURR_DAY_FIRST_RUNHRS 3260
#define LAST_LS_M1_ERR 3262
#define LAST_LS_M2_ERR 3264
#define LAST_BL_M1_ERR 3268
#define LAST_BL_M2_ERR 3270
#define LAST_MN_M1_ERR 3274
#define LAST_MN_M2_ERR 3276
#define LAST_TR_M1_ERR 3280
#define LAST_TR_M2_ERR 3282
#define R_VOL_SP 3284
#define Y_VOL_SP 3286
#define B_VOL_SP 3288
#define METER_ERROR_INTERVAL 3290
#define SINGLE_EPOCH 3292
#define M_STATUS 3294
#define METER_COM_DELAY 3296
#define QUERY_STATUS 3298
#define RESET_RUN_HOURS 3300
#define LOAD_DEFAULT_CONFIG 3302
#define SSL_GSM 3304
#define SSL_CA 3306
#define SSL_CC 3308
#define SSL_CK 3310
#define FILE_CA 3312
#define FILE_CC 3314
#define FILE_CK 3316
#define FILE_UUID 3318
#define FILE_REQ 3320
#define FILE_DEV 3322
#define FILE_NET 3324
#define LOAD_GPRS_CONFIG 3326
#define THREE_PH_SMS 3328
#define EVENT_SMS_DISABLE 3330
#define FIRMWARE 3332
#define SLAVEID 3334
#define GSM_SYNC 3336
#define TIME_UPDATE 3338
#define POLL_REQ3 3340
#define POLL_ERR3 3342
#define WATCHDOG_RESTART 3344
#define MOD_S 3346
#define SIM_S 3348
#define NET_S 3350
#define RTC_S 3352
#define GPRS_S 3354
#define RSSI_S 3356
#define SD_S 3358
#define PF_S 3360
#define FORCEVD_MANUAL 3362
#define MODEM_RESTART 3364
#define SAVE_CONFIG 3366
#define MASTERMOBILE1 3368
#define MASTERMOBILE2 3370
#define POLL_REQ1 3372
#define POLL_ERR1 3374
#define LAST_DATE 3376
#define LAST_TIME 3378
#define SYS_DF 3380
#define DAY_START_TIME 3382
#define SENDACK 3384
#define L_IP1 3386
#define L_IP2 3388
#define L_IP3 3390
#define L_IP4 3392
#define L_MASK1 3394
#define L_MASK2 3396
#define L_MASK3 3398
#define L_MASK4 3400
#define L_GATE1 3402
#define L_GATE2 3404
#define L_GATE3 3406
#define L_GATE4 3408
#define L_DNS1 3410
#define L_DNS2 3412
#define L_DNS3 3414
#define L_DNS4 3416
#define MODULE 3418
#define IP1 3420
#define IP2 3422
#define IP3 3424
#define IP4 3426
#define PORT 3428
#define FTPPORT 3430
#define EEPROMISSUE 3432
#define TEMP 3434
#define GPRS_CHECK_INTERVAL 3436
#define ERROR1 3438
#define ERROR2 3440
#define ERROR3 3442
#define ERROR4 3444
#define ERROR5 3446
#define ERROR6 3448
#define FILE_DELAY 3450
#define SYS_DIAG_FORCE_VD_ENABLE 3452
#define READDO 3454
#define DOMODE 3456
#define TEMP1 3458
#define ERROR12 3460
#define TMCOMM 3462
#define APN 3464
#define USER 3466
#define PASSWORD 3468
#define UPDATE_INTERVAL 3470
#define HEARTBEAT 3472
#define MOBILE1 3474
#define MOBILE2 3476
#define MOBILE3 3478
#define MOBILE4 3480
#define MOBILE5 3482
#define MOBILE6 3484
#define MOBILE7 3486
#define MOBILE8 3488
#define DEFAULT_OVERRIDE 3490
#define BASE_RTC_UPDATE 3492
#define SD_INIT 3494
#define HTTPSPORT 3496
#define DUMMY_SMS 3500
#define ERASE_EEPROM 3502
#define WR_EEPROM 3504
#define READ_EEPROM 3506
#define COUNT_EEPROM_WRITE 3508
#define FTPDOWN 3510
#define AIOFFSET 3512
#define WRITE_EEPROM3 3514
#define WRITE_EEPROM4 3516
#define QOS_FAILCOUNT 3518
#define MAX_QOS_FAILCOUNT 3520
#define DEVICE_STATUS_INV 3522
#define DEVICE_QOS 3524
#define MAX_INVE 3526
#define MAX_DC_CH 3528
#define DUAL_SIM_AUTO 3530
#define POWER_230_MAIN 3532
#define POWER_24_DC 3534
#define POWER_BATTERY 3536
#define BATTERY_MODE_FLAG 3538
#define MODBUS_ERR 3540
#define MODEM_COMM1 3542
#define METER_ERROR_MAX 3544
#define LOGIC_FLAG 3546
#define SEND_DAILY_MSG 3548
#define REG_FLAG 3550
#define DEV_REG_ACT 3552
#define MSG_ID 3554
#define AES_DISABLE 3556
#define FTP_DOWNLOAD 3558
#define VD_STORAGE_TIME 3560
#define VD_STORAGE_TYPE 3562
#define HEARTBEAT_PUSH 3566
#define LAST_DAY_CHANGE 3564
#define ALARM_PUSH 3568
#define HEARTBEAT_TIME 3570
#define DAY_CHANGE_SIM_ENABLE 3572
#define MCU_GPRS_RESET 3574
#define AUTO_TIME_UPDATE_ENABLE 3576
#define RTC_TIME_SAVE 3578
#define VD_LAST_STORAGE_TIME 3580
#define AI1_ERROR 3582
#define AI2_ERROR 3584
#define AI3_ERROR 3586
#define AI4_ERROR 3588
#define AI5_ERROR 3590
#define AI6_ERROR 3592
#define AI1_MODE 3594
#define AI2_MODE 3596
#define AI3_MODE 3598
#define AI4_MODE 3600
#define AI5_MODE 3602
#define AI6_MODE 3604
#define AI1_RESISTOR 3606
#define AI2_RESISTOR 3608
#define AI3_RESISTOR 3610
#define AI4_RESISTOR 3612
#define AI5_RESISTOR 3614
#define AI6_RESISTOR 3616
#define AI1_ENGG_ZERO 3618
#define AI1_ENGG_SPAN 3620
#define AI2_ENGG_ZERO 3622
#define AI2_ENGG_SPAN 3624
#define AI3_ENGG_ZERO 3626
#define AI3_ENGG_SPAN 3628
#define AI4_ENGG_ZERO 3630
#define AI4_ENGG_SPAN 3632
#define AI5_ENGG_ZERO 3634
#define AI5_ENGG_SPAN 3636
#define AI6_ENGG_ZERO 3638
#define AI6_ENGG_SPAN 3640
#define AI1_ELECTRICAL 3642
#define AI2_ELECTRICAL 3644
#define AI3_ELECTRICAL 3646
#define AI4_ELECTRICAL 3648
#define AI5_ELECTRICAL 3650
#define AI6_ELECTRICAL 3652
#define AI1_ENGG 3654
#define AI2_ENGG 3656
#define AI3_ENGG 3658
#define AI4_ENGG 3660
#define AI5_ENGG 3662
#define AI6_ENGG 3664
#define AI1 3666
#define AI2 3668
#define AI3 3670
#define AI4 3672
#define AI5 3674
#define AI6 3676
#define ERR 3678
#define LOAD_DEFAULT_AI 3680
#define POLL_REQ2 3682
#define POLL_ERR2 3684
#define AI1_MF 3686
#define AI2_MF 3688
#define AI3_MF 3690
#define AI4_MF 3692
#define AI5_MF 3694
#define AI6_MF 3696
#define AI1_OFFSET 3698
#define AI2_OFFSET 3700
#define AI3_OFFSET 3702
#define AI4_OFFSET 3704
#define AI5_OFFSET 3706
#define AI6_OFFSET 3708
#define AI1_RAW 3710
#define AI2_RAW 3712
#define AI3_RAW 3714
#define AI4_RAW 3716
#define AI5_RAW 3718
#define AI6_RAW 3720
#define LOAD_CONFIG 3722
#define CONFIG_STORE_FLASH 3724
#define CONFIG_STORE_SD 3726
#define MODBUS_ERR1 3728
#define MODEM_COMM2 3730
#define LAST_QUERY 3732
#define BASETIME_STATUS 3734
#define AUTO_TIME_UPDATE_INTERVAL 3736
#define RTC_UPDATE_TIME 3738
#define WIFI_IDLE_TIME 3740
#define SMS_COUNT 3742
#define SMS_DAILY_LIMIT 3744
#define SPIFFS_ERASE_SIZE 3746
#define SPIFFS_USED 3748
#define FR_WRITE_STATUS2 3750
#define SIM_SLOT_CHANGE_COUNT 3752
#define MODBUS_ERR2 3754
#define MODEM_COMM3 3756
#define SPIFFS_ERROR 3758
#define EPOCH 3760
#define HIST_VD 3762
#define HIST_DATE 3764
#define HIST_INDEX 3766
#define HIST_LOAD 3768
#define HIST_UPLOAD 3770
#define HIST_MSGID 3772
#define SPIFFS_LIST 3774
#define SPIFFS_READ 3776
#define SPIFFS_RDATE 3778
#define SPIFFS_FORMAT 3780
#define SPIFFS_CONFIG_ERASE 3782
#define FORCEVD_COUNT 3784
#define FORCE_ALL 3786
#define READ_FR_DATA 3788
#define FR_ERROR_CODE 3790
#define SPIFFS_ERASE 3792
#define WIFI_STATUS 3794
#define POWER_ON_MIN 3796
#define FR_WD_RESTART 3798
#define PORT_1 3800
#define HIST_EN 3802
#define HIST_ERR 3804
#define DS1307 3806
#define DS1307_DATE 3808
#define DS1307_TIME 3810
#define DS1307_EPOCH 3812
#define DS1307_RTC_UPDATE 3814
#define ESP1_RTC_UPDATE 3816
#define DELAY_RESPONSE 3818
#define DEFAULT_WIFI_MODE 3820
#define DEFAULT_WIFI_MODE_TEMP 3822
#define SD_TRANSFER_TIME 3824
#define SD_TRANSFER_TIME_STAMP 3826
#define SD_TRANSFER_ERROR 3828
#define SD_FORMAT 3830
#define LAST_POFFCNT 3832
#define LAST_POFFTIME_EPOCH 3834
#define POFFTIMEOUT 3836
#define HIST_LIMIT 3838
#define HIST_SENT 3840
#define DEFAULT_WIFI_MODE_TEMP_EN 3842
#define BAUD_115200 3846
#define DEFAULT_WIFI_MODE_OFF 3848
#define SPIFFS_CORRUPT_CMD 3852
#define SPIFFS_CHECK 3854
#define SPIFFS_CHECK_DELAY 3856
#define EEPROM_ERR_COUNT 3858
#define EEPROM_CHECK_DELAY 3860
#define EEPROM_HEALTHY 3862
#define SD_CHECK 3864
#define SD_CHECK_DELAY 3866
#define SD_HEALTHY 3868
#define SD_ERROR 3870
#define SD_CORRUPT_CMD 3872
#define ENABLE_SE2_OLD 3874
#define WINDBOND_DETECTED 3876
#define SPIFFS_TOTAL_SIZE 3878
#define SPIFFS_SET 3880
#define DEVICE_ONTIME 3882
#define DEBUG_EN 3884
#define MODEM_COMM_TEMP 3886
#define DAY_FIRST_DEVICE_ONTIME 3888
#define DLMS_WAIT 3890
#define MUX_SWITCH_TIMEOUT 3892
#define MUX_SWITCH_NEXT_TIMEOUT 3894
#define GET_IMEI1 3896
#define OTA_UPDATE 3898
#define CMD_EN 3900
#define GPSUPDATE 3902
#define LATITUDE 3904
#define LONGITUDE 3906
#define SECURITY_CHECK 3908
#define CONFIG_ERROR 3912
#define METER_FLAG 3914
#define TEMP_REG 3916
#define UPDATE_BATTERY_TIME 3918
#define LAST_PUBLISH_TIME 3920
#define SMS_MAINS_NOTIFY_INTERVAL 3922
#define BATTERY_INTERVAL 3924
#define SMS_PERIODIC_INTERVAL 3926
#define CONNECT_FLAG 3928
#define GPRS_RESTART_ENABLE 3930
#define LOWPF_STATUS 3932
#define LOWPF_THRESHOLD 3934
#define HEARTBEAT_COUNT 3936
#define COTP1 3938
#define POTP1 3940
#define TASK1_STATUS 3946
#define TASK2_STATUS 3948
#define TASK3_STATUS 3950
#define DAY_CHANGE 3952
#define MOUNT_STATUS 3954
#define COTP 3956
#define POTP 3958
#define MUTEX_STATUS 3960
#define REG_TAG 3962
#define REG_TYPE 3964
#define REG_SLAVEID 3966
#define REG_CODE 3968
#define REG_ADD 3970
#define REG_VAL 3972
#define REG_MODBUS_WRITE 3974
#define REG_MODBUS_WRITE_RETRY 3976
#define MAX_RETRY 3978
#define REG_MODBUS_READ 3980
#define REG_ERR_CODE 3982
#define READ_QUERY 3984
#define RSSI1_S 3986
#define RTC_DATE 3988
#define RTC_TIME 3990
#define RTC_TIME_MILLIS 3992
#define RTC_DATE_U 3994
#define RTC_TIME_U 3996
#define RTC_TIME_MILLIS_U 3998
#define RTC_U 4000
#define BMU_DO_UPDATE_AUTO 4002
#define BMU_DO_DEV_ID 4004
#define BMU_DO_NO 4006
#define BMU_DO_VAL 4008
#define WIFI_TX_POWER 4010
#define MILLIS 4012
#define MANUAL_SWITCH 4014
#define SIM 4016
#define AI1_ACT_VALUE 4028
#define AI2_ACT_VALUE 4030
#define AI3_ACT_VALUE 4032
#define AI4_ACT_VALUE 4034
#define AI5_ACT_VALUE 4036
#define AI6_ACT_VALUE 4038
#define AI_OFFSET_CALCULATION 4040
#define AI_CALIBRATION 4042
#define AI_CHANNEL 4044
#define LOAD_UUID 4046
#define MOD_COMM_ERR 4048
#define SIM_DETECT_ERR 4050
#define NET_REG_ERR 4052
#define START_SEQ_ERR 4054
#define ISP_INTERNET_ERR 4056
#define SERV_CONN_ERR 4058
#define GSM_STAGE 4060
#define GPRS_STAGE 4062
#define MQTT_STAGE 4064
#define RESET_GSM_ERR_PARA 4066
#define RESET_SMS_DAY 4068
#define SIM1_SMS_LIMIT 4070
#define SIM2_SMS_LIMIT 4072
#define SIM1_SMS_COUNT 4074
#define SIM2_SMS_COUNT 4076
#define SMS_ERR 4078
#define UPDATE_BAUD 4080
#define RS485_BAUD 4082
#define RS485OVER232 4084
#define ENABLE_DLMS 4086
#define IOT_SOLUTION 4088
#define ENABLE_WDD 4090
#define ENABLE_SEDM 4092
#define ENABLE_WDD_3PH_ONLY 4094
#define COUNT_UUID 4096
#define COUNT_REQ 4098
#define COUNT_DEV 4100
#define COUNT_NET 4102
#define VD1 4104
#define VD2 4106
#define VD3 4108
#define VD4 4110
#define VD5 4112
#define VD6 4114
#define VD7 4116
#define VD8 4118
#define VD9 4120
#define VD10 4122
#define VD11 4124
#define VD12 4126
#define VD13 4128
#define VD14 4130
#define VD15 4132
#define VD16 4134
#define VD17 4136
#define VD18 4138
#define VD19 4140
#define VD20 4142
#define VD21 4144
#define VD22 4146
#define VD23 4148
#define VD24 4150
#define VD25 4152
#define VD26 4154
#define VD27 4156
#define VD28 4158
#define VD29 4160
#define VD30 4162
#define VD28_1 4164
#define VD_TIME1 4168
#define VD_TIME2 4170
#define VD_TIME3 4172
#define VD_TIME4 4174
#define VD_TIME5 4176
#define VD_TIME6 4178
#define VD_TIME7 4180
#define VD_TIME8 4182
#define VD_TIME9 4184
#define VD_TIME10 4186
#define VD_TIME11 4188
#define VD_TIME12 4190
#define VD_TIME13 4192
#define VD_TIME14 4194
#define VD_TIME15 4196
#define VD_TIME16 4198
#define VD_TIME17 4200
#define VD_TIME18 4202
#define VD_TIME19 4204
#define VD_TIME20 4206
#define VD_TIME21 4208
#define VD_TIME22 4210
#define VD_TIME23 4212
#define VD_TIME24 4214
#define VD_TIME25 4216
#define VD_TIME26 4218
#define VD_TIME27 4220
#define VD_TIME28 4222
#define VD_TIME29 4224
#define VD_TIME30 4226
#define VD1_INTERVAL 4232
#define VD2_INTERVAL 4234
#define VD3_INTERVAL 4236
#define VD4_INTERVAL 4238
#define VD5_INTERVAL 4240
#define VD6_INTERVAL 4242
#define VD7_INTERVAL 4244
#define VD8_INTERVAL 4246
#define VD9_INTERVAL 4248
#define VD10_INTERVAL 4250
#define VD11_INTERVAL 4252
#define VD12_INTERVAL 4254
#define VD13_INTERVAL 4256
#define VD14_INTERVAL 4258
#define VD15_INTERVAL 4260
#define VD16_INTERVAL 4262
#define VD17_INTERVAL 4264
#define VD18_INTERVAL 4266
#define VD19_INTERVAL 4268
#define VD20_INTERVAL 4270
#define VD21_INTERVAL 4272
#define VD22_INTERVAL 4274
#define VD23_INTERVAL 4276
#define VD24_INTERVAL 4278
#define VD25_INTERVAL 4280
#define VD26_INTERVAL 4282
#define VD27_INTERVAL 4284
#define VD28_INTERVAL 4286
#define VD29_INTERVAL 4288
#define VD30_INTERVAL 4290
#define VD28_INTERVAL_1 4292
#define DO_WRITE_INTERVEL 4298
#define VD_CONFIG 4300
#define CERT_1_AVAILABLE 4334
#define CERT_2_AVAILABLE 4336
#define CERT_3_AVAILABLE 4338
#define BROKER_CFG_OK 4340
#define CERT1_1_AVAILABLE 4342
#define CERT1_2_AVAILABLE 4344
#define CERT1_3_AVAILABLE 4346
#define BROKER1_CFG_OK 4348
#define GMT_OFFSET 4418
#define DAYLIGHT_OFFSET 4420
#define WIFIONOFFCHECK 4422
#define ENABLE_SE2 4424
#define TIMEOUT_SE2 4426
#define VD_INDEX_SAVE 4428
#define DHCP_DISABLE 4430
#define DHCP_IP1 4432
#define DHCP_IP2 4434
#define DHCP_IP3 4436
#define DHCP_IP4 4438
#define DHCP_MASK1 4440
#define DHCP_MASK2 4442
#define DHCP_MASK3 4444
#define DHCP_MASK4 4446
#define DHCP_GATE1 4448
#define DHCP_GATE2 4450
#define DHCP_GATE3 4452
#define DHCP_GATE4 4454
#define DHCP_DNS1 4456
#define DHCP_DNS2 4458
#define DHCP_DNS3 4460
#define DHCP_DNS4 4462
#define WIFI_RSSI_S 4464
#define WIFI_S 4466
#define WIFI_CONNECT_COUNT 4468
#define WIFI_CONNECT_TIME 4470
#define BROKER_CONNECT_COUNT 4472
#define BROKER_CONNECT_TIME 4474
#define RESET_ENERGY 4476
#define RESET_GT 4478
#define GPRS_EN 4484
#define TAGPERVD 4486
#define DATA_OPT 4488
#define JSON_SIZE_TO_PUSH 4490
#define DATA_OPT_VD_PUSH 4492
#define DATA_OPT_VD_PUSH_TIME 4494
#define STORAGE_SD 4496
#define SD_ERASE_SIZE 4498
#define ACTIVE_STORAGE 4500
#define BUS1_SLAVE 4502
#define DUMMY_TIMEOUT 4508
#define SAVE_BIT 4510
#define FLASH_SAVE 4512
#define ALLDISTATUS 4514
#define TIME_OUT_MOD 4546
#define APPLYRESET 4548
#define FP_SIZE 4550
#define MASTER_MODE 4964
#define MASTER_ADDRESS 4966
#define MASTER_VALUE 4968
#define MASTER_EXECUTION_CMD 4970
#define GSM_AUTO_BAUD_SET 4972
#define GPRS_STATUS 4978
#define FREE_INT 4984
#define LIFE_MIN 4986
#define DUMMY_VAL 4988
#define TIMEOUT_SE3 5040
#define SEL_UUID 5044
#define PHASE_1 5046
#define PHASE_3 5048
#define REG_MODBUS_WRITE_COUNT 5056
#define DEYE_INV 5058
#define DE_DO 5120
#define DE_DLE 5122
#define AUTO_LOAD_EVENT_CONFIG 5124
#define PROCESS_MAS_STATUS 5128
#define WIFI_STATE 5130
#define DEV_QOS 5132
#define WIFI_MODE 5134
#define DELAY_VD_PUSH 5136
#define RTC_FROM_BASE_AUTOUPDATE_ST 5138
#define RTC_BASE_DATE 5140
#define RTC_BASE_TIME 5142
#define RTC_FROM_BASE_RETRY 5144
#define RTC_FROM_BASE_MAX_RETRY 5146
#define UPDATE_CONFIG 5148
#define CURR_DEV 5150
#define WIFI_STATUS1 5160
#define DAY_CHANGE_REST_EN 5162
#define AUTO_INDEX_LOAD 5164
#define AUTO_INDEX_SET 5166
#define RTC_CLK_EN_32K 5228
#define CONFIG_TIMEOUT 5230
#define CONFIG_RID_1 5232
#define CONFIG_RID_2 5234
#define CONFIG_TOTAL 5236
#define CONFIG_PAGE 5238
#define CONFIG_DATA_READY 5240
#define CONFIG_BIT_WISE 5242
#define CONFIG_FILE_ERASE 5244
#define TIMEOUT_RID 5246
#define CONFIG_READ 5248
#define CONFIG_FILE_READ 5250
#define SE2_REG_DATATYPE_1 5252
#define SE2_REG_SLAVEID_1 5254
#define SE2_REGISTER_ADDRESS_1 5256
#define SE2_REG_VALUE_1 5258
#define SEND_RESPONSE 5260
#define WIFI_CHANGE 5262
#define SE2_REG_DATATYPE 5292
#define SE2_REG_SLAVEID 5294
#define SE2_REGISTER_ADDRESS 5296
#define SE2_WRITE_REGISTER 5298 
#define SE2_READ_REGISTER 5300
#define SE2_REG_VALUE 5302
#define SE2_DATA 5304
#define DUMMY_DEVID 5306
#define SE2_REGISTER_ID 5308
#define REG_DATA_BACKUP 5310
#define REG_DATA_BACKUP_SA 5312
#define REG_DATA_BACKUP_LENGTH 5314
#define TEST_DO 5320
#define CONTEXT_SIM 5322
#define CONTEXT_DIS 5324
#define RET_CONTEXT_DIS 5326
#define MD_RESET 5328
#define METER_EXECUTE_CMD 5330
#define METER_MODE 5334
#define METER_ADDRESS 5336
#define METER_VALUE 5338
#define FLAGC1 5360
#define DELAY_NWREG 5362
#define WIFI_TIME 5364
#define POLL_REQ_TEMP 5366
#define POLL_ERR_TEMP 5368
#define BUS2_ERROR 5370
#define BUS2_ERROR_TOT 5372
#define CONFIG_SAVE_TO_CORE 5374
#define CRC_RESULT 5376
#define CRC_FR_STORE 5378
#define NVS_INIT_DATASTORE 5380
#define ENABLE_BUSID_2 5382
#define ENABLE_SEDM_2 5384
#define ALRM_BIT 5390
#define ALRM_VD 5392
#define ALARM_UUID_VAL 5394
#define FR_STORE 5396
#define ALRM_TM 5398
#define ALRM_TMOUT 5400
#define DO_RETRY 5402
#define DEV_ID 5404
#define JSON_UPDATE 5406
#define LAST_NVS_ERR 5408
#define NVS_ERR_CNT 5410
#define FLAG 5412
#define MODSTATUS 5414
#define GPRS_ACTIVE 5416
#define CONNECT_TRY 5418
#define BROKER_CONNECT 5420
#define DEVICE_REG 5422
#define BATTERY_MODE 5424
#define OTP_EN 5426
#define CERT_RENEW_DATE_1 5430
#define CERT_EXPIRY_DATE_1 5432
#define CERT_1 5434
#define CERT_CNT_1 5436
#define CERT_EPOCH_1 5438
#define CERT_PROCESS_ST_1 5440
#define CERT_C_1 5444
#define CERT_ON_DLY_EPOCH_1 5446
#define CERT_ACK_1 5450
#define HIST_ERR_1 5452
#define HIST_VD_1 5454 
#define HIST_UPDATE_VD_1 5456
#define INFO_TOPIC_1 5498
#define THREAD1 5500
#define THREAD2 5502
#define IIOT_NUM 5638
#define IIOT_NUM_1 5640
#define INFO_TOPIC 5642
#define QOS_EN 5644
#define IS_1_0_ST 5648
#define ASN_31 5650
#define CURRENT_COUNT 5652
#define DATABIT 5654
#define STOPBIT 5656
#define PARITY 5658
#define BAUD 5660
#define NET_SETBIT 5662
#define SMS_ENABLE_COUNT 5664
#define SIM_ENABLE_COUNT 5666
#define SMS_TIME 5668
#define NUMBER1 5670
#define NUMBER2 5672
#define CERT_RENEW_DATE 5676
#define CERT_EXPIRY_DATE 5678
#define CERT 5680
#define CERT_CNT 5682
#define CERT_PROCESS_ST 5684
#define CERT_DELAY 5686
#define CERT_EPOCH 5688
#define CERT_C 5690
#define CERT_ON_DLY_EPOCH 5692
#define CERT_ON_DLY 5694
#define CERT_ACK 5696
#define GPRS_START 5698
#define CID_SET 5700
#define CID_SET_1 5702
#define DEL_CERT 5704
#define SERVER_CONNECTION 5706
#define SSL_CA_1 5708
#define SSL_CC_1 5710
#define SSL_CK_1 5712
#define MQTT_STAGE_C1 5714
#define CONNECT_TRY_C1 5716
#define SERV_CONN_ERR_C1 5718
#define DEV_REG_ACT_C1 5720
#define CONNECTION_C1 5724
#define DEVICE_REG_C1 5726
#define BROKER_CONNECT_C1 5728
#define ERROR1_C1 5730
#define SSL_GSM_C1 5732
#define HEARTBEAT_PUSH_C1 5734
#define HEARTBEAT_TIME_C1 5736
#define BROKER_CONNECT_COUNT_C1 5738
#define BROKER_CONNECT_TIME_C1 5740
#define HIST_LOAD_C1 5742
#define HIST_UPLOAD_C1 5744
#define HIST_VD_C1 5746
#define HIST_DATE_C1 5748
#define HIST_INDEX_C1 5750
#define FLAG_C1 5752
#define BATTERY_MODE_FLAG_C1 5754
#define BATTERY_MODE_C1 5756
#define IOT_SOLUTION_C1 5758
#define LAST_PUBLISH_TIME_C1 5760
#define HIST_UPDATE_VD 5762
#define LAST_HIST_CHECK_TIME 5764
#define LAST_HIST_CHECK_TIME_2 5766
#define LAST_HIST_CHECK 5768
#define SLD_TIMEOUT 5770
#define SLD_CONT_SENDING_DATA 5772
#define SLD_TIMEOUT_STOP_S 5774
#define SLD_TIMEOUT_NEXT_EPOCH 5776
#define SLD_INTERVAL 5778
#define SLD_TIMEOUTFORSTOPSENDINGDATA 5780
#define ENERYGY_PUSH_3 5782
#define ENERYGY_PUSH_4 5784
#define ENERYGY_PUSH_3_1 5786
#define ENERYGY_PUSH_4_1 5788
#define SLD_TIMEOUT_1 5790
#define SLD_CONT_SENDING_DATA_1 5792
#define OFF_REG_ADD 5800
#define OFF_VALUE_BITWISE_CHOOSE 5802
#define OFF_VALUE_BITWISE_STORAGE 5804
#define OFF_INVERTOR_METHOD 5806
#define ON_REG_ADD 5814
#define ON_VALUE_BITWISE_CHOOSE 5816
#define ON_VALUE_BITWISE_STORAGE 5818
#define ON_INVERTOR_METHOD 5820
#define FAULT_REG_ADD 5828
#define FAULT_VALUE_BITWISE_CHOOSE 5830
#define FAULT_VALUE_BITWISE_STORAGE 5832
#define FAULT_INVERTOR_METHOD 5834
#define OTHERS_REG_ADD 5842
#define OTHERS_VALUE_BITWISE_CHOOSE 5844
#define OTHERS_VALUE_BITWISE_STORAGE 5846
#define OTHERS_INVERTOR_METHOD 5848
#define SWITCH_EN_REG 5856
#define SWITCH_EN 5858
#define SWITCH_EN_REG_ADD 5860
#define SWITCH_EN_VALUE_BITWISE_CHOOSE 5862
#define SWITCH_EN_VALUE_BITWISE_STORAGE 5864
#define SWITCH_DIS_REG_ADD 5866
#define SWITCH_DIS_VALUE_BITWISE_CHOOSE 5868
#define SWITCH_DIS_VALUE_BITWISE_STORAGE 5870
#define CONTROL_ON_REG_ADD 5872
#define CONTROL_ON_VALUE_BITWISE_CHOOSE 5874
#define CONTROL_ON_VALUE_BITWISE_STORAGE 5876
#define CONTROL_OFF_REG_ADD 5878
#define CONTROL_OFF_VALUE_BITWISE_CHOOSE 5880
#define CONTROL_OFF_VALUE_BITWISE_STORAGE 5882
#define EMERGENCY_SHUTDOWN_REG_ADD 5884
#define EMERGENCY_SHUTDOWN_VALUE_BITWISE_CHOOSE 5886
#define EMERGENCY_SHUTDOWN_VALUE_BITWISE_STORAGE 5888
#define CLOCK_ERROR_CODE 5800
#define CLOCK_START_ADDRESS 5802
#define REGISTER_ERROR_CODE 5808
#define REGISTER_START_ADDRESS 5810
#define CLOCK_ERROR_CODE_2 5930
#define CLOCK_START_ADDRESS_2 5932
#define REGISTER_ERROR_CODE_2 5938
#define REGISTER_START_ADDRESS_2 5940
#define DATA_ERROR_CODE 6090
#define DATA_ERROR_CODE_2 6092
#define STRING_START_ADDRESS 6140
#define STRING_START_ADDRESS_2 6286
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
            addr = int(parts[2])
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

def build_ondemand_payload(reg_name, reg_val=None, cmkey="155521", pmkey="438266", cmd="read", custom_timestamp=None, batch_dict=None):
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
