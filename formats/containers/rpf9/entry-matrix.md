# RPF9 entry matrix

Machine-written from a `lforge archive census` run. Every row is one
combination of properties observed in the sample: the entry type stored in
the table of contents, the identification made from the decoded head, the
storage shape, whether the payload transform applies, whether the payload
decoded, the confidence of the identification, what the application can do
with the entry, and the extension the classification allowed.

- roots: `anim.rpf`, `appdata0.rpf`, `audio.rpf`, `common.rpf`, `data.rpf`, `levels.rpf`, `movies.rpf`, `navmeshes.rpf`, `packs.rpf`, `script.rpf`, `shaders.rpf`, `textures.rpf`
- archives opened: 69
- entries classified: 8138
- stopped early: anim.rpf: max_entries, audio.rpf: max_entries, data.rpf: max_entries, levels.rpf: max_entries, navmeshes.rpf: max_entries, packs.rpf: max_entries, script.rpf: max_entries, textures.rpf: max_entries

## Every combination

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 0 | format:rpf9 | stored | no | decoded | probable | archive | rpf | 57 |
| 2 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 367 |
| 3 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 224 |
| 5 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 884 |
| 6 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 292 |
| 11 | format:psin | chunked-3 | no | decoded | verified | structural | - | 897 |
| 11 | format:rbf0 | raw-deflate | no | decoded | verified | structural | - | 156 |
| 66 | format:gfx | chunked-3 | no | decoded | verified | structural | - | 5 |
| 67 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 735 |
| 70 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 26 |
| 74 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 6 |
| 79 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 899 |
| 87 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 132 |
| 89 | none | chunked-2 | yes | transform-failed | unknown | unavailable | - | 1 |
| 93 | format:psin | chunked-3 | no | decoded | verified | structural | - | 37 |
| 94 | format:psin | chunked-3 | no | decoded | verified | structural | - | 19 |
| 95 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 421 |
| 96 | none | chunked-3 | no | decoded | unknown | bytes | - | 1 |
| 102 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 1 |
| 111 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 732 |
| 114 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 421 |
| 255 | format:adat | stored | no | decoded | verified | structural | - | 887 |
| 255 | format:kb2 | stored | no | decoded | verified | structural | - | 515 |
| 255 | xml:timecycle_modifier_data | chunked-3 | no | decoded | verified | text | xml | 49 |
| 255 | xml:rage__bgCrackType | chunked-3 | yes | decoded | verified | text | xml | 36 |
| 255 | xml:CVehiclePoints | chunked-3 | no | decoded | verified | text | xml | 32 |
| 255 | xml:timecycle_keyframe_data | chunked-3 | no | decoded | verified | text | xml | 27 |
| 255 | xml:CTuningFile | chunked-3 | yes | decoded | verified | text | xml | 24 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | no | decoded | verified | text | xml | 23 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | yes | decoded | verified | text | xml | 21 |
| 255 | xml:CTuningFile | chunked-3 | no | decoded | verified | text | xml | 10 |
| 255 | none | chunked-3 | yes | decoded | unknown | bytes | - | 9 |
| 255 | none | chunked-3 | no | decoded | unknown | bytes | - | 8 |
| 255 | xml:WaveData | chunked-3 | yes | decoded | verified | text | xml | 6 |
| 255 | xml:CDamageDataManager | chunked-3 | no | decoded | verified | text | xml | 5 |
| 255 | xml:GridAtlasInfo | chunked-3 | no | decoded | verified | text | xml | 4 |
| 255 | xml:CCoverProcessorTuning | chunked-3 | no | decoded | verified | text | xml | 3 |
| 255 | format:psin | chunked-3 | yes | decoded | verified | structural | - | 2 |
| 255 | signature:Observed("mhiu") | chunked-3 | no | decoded | verified | bytes | - | 2 |
| 255 | signature:Observed("sgd5") | stored | no | decoded | verified | bytes | - | 2 |
| 255 | xml:CDataFileMgr__ContentDef | chunked-3 | no | decoded | verified | text | xml | 2 |
| 255 | xml:CVehiclePerformanceMaps | chunked-3 | no | decoded | verified | text | xml | 2 |
| 255 | xml:VehicleControlsInfo | chunked-3 | yes | decoded | verified | text | xml | 2 |
| 255 | xml:unvalidated | chunked-3 | no | decoded | tentative | text | - | 2 |
| 255 | signature:Observed("sps1") | chunked-3 | no | decoded | verified | bytes | - | 1 |
| 255 | xml:ActionCoordinator__ActionCoordinatorData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:BoatHullBlackList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CAimUpperBodyDataBlock | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimSceneAttachSlotSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimalAnimationContexts | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimalAttackBehaviours | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAttachmentSlotData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CBaitingInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CBodyAnimConstraintInfoStateSetManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CBreakableVehicleDoorLockManagerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CClimbTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CCombatInfoMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CContentsOfWeatherXmlFile | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CConversationDictionary | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CConversationList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CDiscoverableCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CDoorInteractionDataList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CDrivingStyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CDynamicScenarioManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CEnergyConfigInfos | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CEntityComponentLodManagerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CFallenSnowData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CFiringPatternInfoManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CFleeDecisionMakerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CFluidVesselManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CGarageInitDataList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CGraphicsDefinitionsData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHazardNodes | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHeadbobConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHealthConfigInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CIdlePreferenceManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLadderMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLadderRailsMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLassoDataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMissions | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMoodConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMovieQualityVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CObjectComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPairedPedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CParkingSplines | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedAccuracyManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedArmourMetaData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedBreathingTypes | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedDensityScoringConfigMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedFormationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedHeadbobSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedInventoryLoadOutManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMoodConditionTreesManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMoodSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMotivationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedScheduleInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedSpeedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedTimeWarpSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedVariationBodyTypeManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPersonaEnumValuesMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPlayerDiscoverableDataCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CProceduralInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CScatteringTransmittance__FogVolumeListData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CScenarioPropDataManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CSceneTerrainAnalyzerMgrDataInstance | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CScenicViewManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CSearchPointOfInterestRuleSet | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CSnowTrackData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CStandardPosesManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTVPlaylistContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTacticalAnalysisDistributionStore | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTaskDataInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTaskMoveLocalMovement__Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CTrainConfigs | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTyreDataSet | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CUpperBodyIdleConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CUpperBodyIdleSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleAIHandlingEntry | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleBaseRatingsAndEstimatesMap | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleBoneOffsetsArray | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleDistantLightData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehiclePointsMeta | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CWeaponActionHashToIndexMappings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Clock__Filter__Presets | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Combat__GoalData__Store | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Combat__Settings__ActionStore | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Confront__StyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CoverShadowTunables | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CustomClouds | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:DiffractionProfiles | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:EnvironmentalWaterDisturbManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:FogVolumeProfileList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:GameShape__Data__LocationNameLoopkup | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:GameShape__Data__ManagerSettings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:GlintsProfiles | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:InteractionFoam_Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:InteriorGroups | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:LUTColorblindnessVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:LandingPageVideos | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:LightAnimationPresets | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:LostTargetSearch__Tunables | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:MainWaterTune | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:MapState__Data__Templates | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:MaterialDataList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Mindset__CMindsetDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:ModelTagMappings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:ModelTags | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Modular__SM__AIBehaviour__LockControllerConfig | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:OceanSimPresets | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:OceanWaveCalmingCurves | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PatchConstants | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PathingStyleData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PedMotion__PedMotionData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:PostFXSpline__Store | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:PromptInternal__PromptTunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:RegionTintMap | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Relationships__GroupsData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Respawn__MetaData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:RumbleProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SMandatoryPacksData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SSetupData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STPedMotionPredictionSetContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STPedNavigationPredictiontPresetContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STS_Config | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:ShoreWavePlacementData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:SoftBoundTuningList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SpecialAbilityTagTargetsSettings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Sprinklers__RootData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:StudioConfigurationData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Tactical__PointValidation__DataStore | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TextureGridInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:TyreProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:VehicleFragImpulseFunction | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:WalkAndTalkProfileData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:WaterTessellationSettings__AllAllowancesAndThresholds | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:WeaponAnimations__ConfigData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:WeaponAnimations__FullbodyControllerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Witnesses__Informations | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:aiNavIMapGroupData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:hrsSimTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:naSpeechEventTypeBatchRequestParams | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__MediaDecoderSettings | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__bgConfig | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__crRetarget__SolversTunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__fragTuneStruct | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__fwRetargetCoordinatorConfig | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__phMBS_MaterialParamsDatabase_Def | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:sCollisionEventScannerTuning | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:sPedDamageModifiers | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:sPedDistractionModifiers | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:time_data | chunked-3 | no | decoded | verified | text | xml | 1 |

## By entry type

### Type 0: 57 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 0 | format:rpf9 | stored | no | decoded | probable | archive | rpf | 57 |

Samples:
- `anim.rpf!0`: 6912 bytes, head `39465052c00200009002000010010000eea950ee299baea7007a040050010000`
- `anim.rpf!1`: 858672 bytes, head `39465052800d0000000c0000300a000049e5e4d63ebd6f79007a040050010000`
- `anim.rpf!2`: 151120 bytes, head `39465052200b000080070000502e00003fec8c787656199b007a040050010000`
- `audio.rpf!0`: 143174144 bytes, head `39465052400f0000c00c0000e00800005b25daca02127b1d007a040050010000`

### Type 2: 367 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 2 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 367 |

Samples:
- `levels.rpf!2!0`: 1603856 bytes, head `0000000000000000c070045000000000005a0450000000000000000000000000`
- `levels.rpf!2!2`: 354048 bytes, head `0000000000000000307600500000000080740050000000000000000000000000`
- `levels.rpf!2!3`: 945120 bytes, head `000000000000000090da01500000000010d50150000000000000000000000000`

### Type 3: 224 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 3 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 224 |

Samples:
- `levels.rpf!5!0`: 11456 bytes, head `0000000000000000d017005000000000e00a005000000000b006005000000000`
- `levels.rpf!5!1`: 75344 bytes, head `00000000000000005039005000000000901f0050000000009018005000000000`
- `levels.rpf!5!2`: 69776 bytes, head `00000000000000001044005000000000c022005000000000901e005000000000`

### Type 5: 884 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 5 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 884 |

Samples:
- `data.rpf!1!0`: 95104 bytes, head `0000000000000000700200500000000000000000000000000100000000000000`
- `data.rpf!1!1`: 84224 bytes, head `0000000000000000100700500000000000000000000000000100000000000000`
- `data.rpf!1!2`: 197008 bytes, head `0000000000000000200100500000000000000000000000000100000000000000`
- `textures.rpf!0!0`: 2557072 bytes, head `0000000000000000900300500000000000000000000000000100000000000000`

### Type 6: 292 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 6 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 292 |

Samples:
- `levels.rpf!2!1`: 73872 bytes, head `000000000000000060fa005000000000060100000ea742420000000000000000`
- `levels.rpf!2!5`: 31840 bytes, head `0000000000000000a07b005000000000060100004a0a80420000000000000000`
- `levels.rpf!2!10`: 147824 bytes, head `0000000000000000304102500000000006010000105e44420000000000000000`

### Type 11: 1053 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 11 | format:psin | chunked-3 | no | decoded | verified | structural | - | 897 |
| 11 | format:rbf0 | raw-deflate | no | decoded | verified | structural | - | 156 |

Samples:
- `data.rpf!2!321`: 7176 bytes, head `5053494e000007f0808637b730000000aaaaaaaaaaaaaaaa4a00000090070000`
- `script.rpf!1!0`: 3520 bytes, head `5053494e000005f016000000b0000000aaaaaaaaaaaaaaaad823b6ae54000000`
- `script.rpf!1!1`: 119296 bytes, head `5053494e0001913016000000c8060000aaaaaaaaaaaaaaaad823b6aec80a0000`
- `script.rpf!1!2`: 2336 bytes, head `5053494e000003a01600000058000000aaaaaaaaaaaaaaaad823b6ae18000000`

### Type 66: 5 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 66 | format:gfx | chunked-3 | no | decoded | verified | structural | - | 5 |

Samples:
- `data.rpf!1!3`: 21133 bytes, head `4746582a8d52000070000b540000b540001e01001bfa0104000000000e00000f`
- `data.rpf!1!4`: 12107 bytes, head `4746582a4b2f00008000026d4000018600001e010013fa0104000000000e0000`
- `data.rpf!1!5`: 1379793 bytes, head `4746582ad10d15008800012c0000002a3000001e010011fa0104000000000e00`

### Type 67: 735 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 67 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 735 |

Samples:
- `anim.rpf!5!0`: 73424 bytes, head `0000000000000000f01d01500000000000000000000000000000000000000000`
- `anim.rpf!5!1`: 421776 bytes, head `0000000000000000e06d06500000000000000000000000000000000000000000`
- `anim.rpf!5!2`: 13696 bytes, head `0000000000000000903400500000000000000000000000000000000000000000`

### Type 70: 26 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 70 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 26 |

Samples:
- `anim.rpf!0!0`: 16368 bytes, head `0000000000000000d03800500000000000000000000000000000000000000000`
- `anim.rpf!2!0`: 6576 bytes, head `0000000000000000701800500000000000000000000000000000000000000000`
- `anim.rpf!2!1`: 12064 bytes, head `0000000000000000b02c00500000000000000000000000000000000000000000`

### Type 74: 6 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 74 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 6 |

Samples:
- `levels.rpf!0!0`: 189440 bytes, head `00000000000000005085025000000000304452507a0000000000000000000000`
- `levels.rpf!0!1`: 177456 bytes, head `00000000000000007064025000000000304452507a0000000000000000000000`
- `levels.rpf!0!2`: 131072 bytes, head `0000000000000000207e015000000000304452507a0000000000000000000000`

### Type 79: 899 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 79 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 899 |

Samples:
- `navmeshes.rpf!0!0`: 141040 bytes, head `0000000000000000702602500000000009000000150001000000000000000000`
- `navmeshes.rpf!0!1`: 393216 bytes, head `000000000000000080f405500000000003000000150001000000000000000000`
- `navmeshes.rpf!0!2`: 136784 bytes, head `0000000000000000d01502500000000009000000150001000000000000000000`

### Type 87: 132 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 87 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 132 |

Samples:
- `anim.rpf!1!0`: 255200 bytes, head `0000000000000000506d035000000000304452507a0000000000000000000000`
- `anim.rpf!1!1`: 203120 bytes, head `000000000000000070be025000000000304452507a0000000000000000000000`
- `anim.rpf!1!2`: 241920 bytes, head `0000000000000000403a035000000000304452507a0000000000000000000000`

### Type 89: 1 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 89 | none | chunked-2 | yes | transform-failed | unknown | unavailable | - | 1 |

Samples:
- `script.rpf!0!0`: - bytes, head ``

### Type 93: 37 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 93 | format:psin | chunked-3 | no | decoded | verified | structural | - | 37 |

Samples:
- `packs.rpf!1!0`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!1`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!5`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`

### Type 94: 19 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 94 | format:psin | chunked-3 | no | decoded | verified | structural | - | 19 |

Samples:
- `packs.rpf!1!2`: 344 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!3`: 360 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!4`: 360 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`

### Type 95: 421 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 95 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 421 |

Samples:
- `packs.rpf!0!0`: 12160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`
- `packs.rpf!0!2`: 12160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`
- `packs.rpf!0!4`: 12160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`

### Type 96: 1 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 96 | none | chunked-3 | no | decoded | unknown | bytes | - | 1 |

Samples:
- `script.rpf!0!1`: 2702384 bytes, head `0000000000000000000000000000000000000000db7700000000000000000000`

### Type 102: 1 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 102 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 1 |

Samples:
- `anim.rpf!3!0`: 29648 bytes, head `0000000000000000707000500000000000000000000000000000000000000000`

### Type 111: 732 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 111 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 732 |

Samples:
- `data.rpf!2!0`: 1840 bytes, head `0000000000000000e005005000000000304452507a0000000000000000000000`
- `data.rpf!2!1`: 26464 bytes, head `00000000000000001066005000000000304452507a0000000000000000000000`
- `data.rpf!2!2`: 27264 bytes, head `00000000000000003069005000000000304452507a0000000000000000000000`

### Type 114: 421 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 114 | resource:segment-5 | chunked-2 | no | decoded | probable | resource | - | 421 |

Samples:
- `packs.rpf!0!1`: 1114288 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`
- `packs.rpf!0!3`: 4849840 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`
- `packs.rpf!0!5`: 1114288 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`

### Type 255: 1825 entries

| Type | Identification | Storage | Transform | Payload | Confidence | Capability | Extension | Entries |
| ---- | -------------- | ------- | --------- | ------- | ---------- | ---------- | --------- | ------: |
| 255 | format:adat | stored | no | decoded | verified | structural | - | 887 |
| 255 | format:kb2 | stored | no | decoded | verified | structural | - | 515 |
| 255 | xml:timecycle_modifier_data | chunked-3 | no | decoded | verified | text | xml | 49 |
| 255 | xml:rage__bgCrackType | chunked-3 | yes | decoded | verified | text | xml | 36 |
| 255 | xml:CVehiclePoints | chunked-3 | no | decoded | verified | text | xml | 32 |
| 255 | xml:timecycle_keyframe_data | chunked-3 | no | decoded | verified | text | xml | 27 |
| 255 | xml:CTuningFile | chunked-3 | yes | decoded | verified | text | xml | 24 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | no | decoded | verified | text | xml | 23 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | yes | decoded | verified | text | xml | 21 |
| 255 | xml:CTuningFile | chunked-3 | no | decoded | verified | text | xml | 10 |
| 255 | none | chunked-3 | yes | decoded | unknown | bytes | - | 9 |
| 255 | none | chunked-3 | no | decoded | unknown | bytes | - | 8 |
| 255 | xml:WaveData | chunked-3 | yes | decoded | verified | text | xml | 6 |
| 255 | xml:CDamageDataManager | chunked-3 | no | decoded | verified | text | xml | 5 |
| 255 | xml:GridAtlasInfo | chunked-3 | no | decoded | verified | text | xml | 4 |
| 255 | xml:CCoverProcessorTuning | chunked-3 | no | decoded | verified | text | xml | 3 |
| 255 | format:psin | chunked-3 | yes | decoded | verified | structural | - | 2 |
| 255 | signature:Observed("mhiu") | chunked-3 | no | decoded | verified | bytes | - | 2 |
| 255 | signature:Observed("sgd5") | stored | no | decoded | verified | bytes | - | 2 |
| 255 | xml:CDataFileMgr__ContentDef | chunked-3 | no | decoded | verified | text | xml | 2 |
| 255 | xml:CVehiclePerformanceMaps | chunked-3 | no | decoded | verified | text | xml | 2 |
| 255 | xml:VehicleControlsInfo | chunked-3 | yes | decoded | verified | text | xml | 2 |
| 255 | xml:unvalidated | chunked-3 | no | decoded | tentative | text | - | 2 |
| 255 | signature:Observed("sps1") | chunked-3 | no | decoded | verified | bytes | - | 1 |
| 255 | xml:ActionCoordinator__ActionCoordinatorData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:BoatHullBlackList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CAimUpperBodyDataBlock | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimSceneAttachSlotSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimalAnimationContexts | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAnimalAttackBehaviours | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CAttachmentSlotData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CBaitingInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CBodyAnimConstraintInfoStateSetManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CBreakableVehicleDoorLockManagerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CClimbTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CCombatInfoMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CContentsOfWeatherXmlFile | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CConversationDictionary | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CConversationList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CDiscoverableCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CDoorInteractionDataList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CDrivingStyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CDynamicScenarioManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CEnergyConfigInfos | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CEntityComponentLodManagerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CFallenSnowData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CFiringPatternInfoManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CFleeDecisionMakerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CFluidVesselManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CGarageInitDataList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CGraphicsDefinitionsData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHazardNodes | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHeadbobConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CHealthConfigInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CIdlePreferenceManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLadderMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLadderRailsMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CLassoDataManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMissions | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMoodConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CMovieQualityVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CObjectComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPairedPedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CParkingSplines | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedAccuracyManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedArmourMetaData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedBreathingTypes | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedDensityScoringConfigMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPedFormationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedHeadbobSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedInventoryLoadOutManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMoodConditionTreesManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMoodSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedMotivationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedScheduleInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedSpeedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedTimeWarpSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPedVariationBodyTypeManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CPersonaEnumValuesMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CPlayerDiscoverableDataCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CProceduralInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CScatteringTransmittance__FogVolumeListData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CScenarioPropDataManager | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CSceneTerrainAnalyzerMgrDataInstance | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CScenicViewManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CSearchPointOfInterestRuleSet | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CSnowTrackData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CStandardPosesManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTVPlaylistContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTacticalAnalysisDistributionStore | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTaskDataInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTaskMoveLocalMovement__Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CTrainConfigs | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CTyreDataSet | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CUpperBodyIdleConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CUpperBodyIdleSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleAIHandlingEntry | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleBaseRatingsAndEstimatesMap | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleBoneOffsetsArray | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehicleDistantLightData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CVehiclePointsMeta | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CWeaponActionHashToIndexMappings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Clock__Filter__Presets | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Combat__GoalData__Store | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Combat__Settings__ActionStore | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Confront__StyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:CoverShadowTunables | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:CustomClouds | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:DiffractionProfiles | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:EnvironmentalWaterDisturbManager | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:FogVolumeProfileList | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:GameShape__Data__LocationNameLoopkup | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:GameShape__Data__ManagerSettings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:GlintsProfiles | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:InteractionFoam_Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:InteriorGroups | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:LUTColorblindnessVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:LandingPageVideos | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:LightAnimationPresets | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:LostTargetSearch__Tunables | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:MainWaterTune | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:MapState__Data__Templates | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:MaterialDataList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Mindset__CMindsetDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:ModelTagMappings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:ModelTags | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Modular__SM__AIBehaviour__LockControllerConfig | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:OceanSimPresets | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:OceanWaveCalmingCurves | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PatchConstants | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PathingStyleData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:PedMotion__PedMotionData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:PostFXSpline__Store | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:PromptInternal__PromptTunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:RegionTintMap | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Relationships__GroupsData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Respawn__MetaData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:RumbleProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SMandatoryPacksData | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SSetupData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STPedMotionPredictionSetContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STPedNavigationPredictiontPresetContainer | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:STS_Config | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:ShoreWavePlacementData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:SoftBoundTuningList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:SpecialAbilityTagTargetsSettings | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:Sprinklers__RootData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:StudioConfigurationData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Tactical__PointValidation__DataStore | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:TextureGridInfo | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:TyreProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:VehicleFragImpulseFunction | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:WalkAndTalkProfileData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:WaterTessellationSettings__AllAllowancesAndThresholds | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:WeaponAnimations__ConfigData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:WeaponAnimations__FullbodyControllerData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:Witnesses__Informations | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:aiNavIMapGroupData | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:hrsSimTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:naSpeechEventTypeBatchRequestParams | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__MediaDecoderSettings | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__bgConfig | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__crRetarget__SolversTunables | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__fragTuneStruct | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:rage__fwRetargetCoordinatorConfig | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:rage__phMBS_MaterialParamsDatabase_Def | chunked-3 | yes | decoded | verified | text | xml | 1 |
| 255 | xml:sCollisionEventScannerTuning | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:sPedDamageModifiers | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:sPedDistractionModifiers | chunked-3 | no | decoded | verified | text | xml | 1 |
| 255 | xml:time_data | chunked-3 | no | decoded | verified | text | xml | 1 |

Samples:
- `audio.rpf!0!0`: 315488 bytes, head `41444154010025ff020000004000000000000300a54329040000000018811d53`
- `audio.rpf!0!1`: 102496 bytes, head `41444154010025ff020000004000000000000300a54329040000000028c8b652`
- `audio.rpf!0!2`: 92256 bytes, head `41444154010025ff020000004000000000000300a5432904000000009340d4d4`
- `movies.rpf!0`: 1866836 bytes, head `4b42326e4c7c1c008c000000244b00008c00000000050000d00200001e000000`

