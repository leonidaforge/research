# RPF9 entry matrix

Machine-written from a `lforge archive census` run. Every row is one
combination of properties observed in the run: the entry type stored in
the table of contents, the identification made from the decoded head, a
normalised shape of that head, the storage shape, whether the payload
transform applies, whether the payload decoded, whether the structure was
validated, what the application can do with the entry, the extension the
classification allowed and where that extension came from.

## Coverage

| Count | Value |
| ----- | ----: |
| roots_discovered | 22 |
| roots_opened | 22 |
| failed_roots | 0 |
| archives_opened | 4,373 |
| nested_archives_opened | 4,351 |
| failed_archives | 0 |
| rejected_archive_candidates | 0 |
| entries_enumerated | 1,255,039 |
| entries_probed | 1,255,039 |
| entries_decoded | 1,255,039 |
| entries_undecoded | 0 |
| structures_verified | 93,631 |
| containers_identified | 1,153,560 |
| declared_asset_classes | 1,181,971 |
| unresolved_formats | 3,047 |
| stopped early | nothing |
| complete | True |

A bounded run is a sample. Only a run whose coverage reports every
discovered root and no stopped scan is a count of the installation.

## By root

| Root | Archives | Entries | Stopped |
| ---- | -------: | ------: | ------- |
| anim.rpf | 236 | 84,940 | - |
| appdata0.rpf | 1 | 2 | - |
| audio.rpf | 104 | 7,283 | - |
| common.rpf | 1 | 418 | - |
| data.rpf | 42 | 23,075 | - |
| levels.rpf | 2,051 | 526,538 | - |
| movies.rpf | 1 | 515 | - |
| navmeshes.rpf | 29 | 64,779 | - |
| pack/core_bvh4/core_bvh4.rpf | 1,282 | 295,244 | - |
| pack/core_licenses/core_licenses_data.rpf | 2 | 6 | - |
| pack/core_restofworld/core_restofworld.rpf | 11 | 1,156 | - |
| pack/core_restofworld001/core_restofworld001.rpf | 2 | 28 | - |
| pack/shared_minigame000/shared_minigame000.rpf | 50 | 3,183 | - |
| pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf | 9 | 1,331 | - |
| pack/story000/story000.rpf | 442 | 160,082 | - |
| pack/story000/story000_script.rpf | 5 | 3,072 | - |
| pack/story000_bvh4/story000_bvh4.rpf | 1 | 4 | - |
| pack/story000_restofworld/story000_restofworld.rpf | 19 | 507 | - |
| packs.rpf | 60 | 80,470 | - |
| script.rpf | 3 | 1,016 | - |
| shaders.rpf | 1 | 3 | - |
| textures.rpf | 21 | 1,387 | - |

## Completion

| Check | Value |
| ----- | ----- |
| complete | 1 |
| reasons | none |
| pending traversal | - |

## Outcomes

Every entry has exactly one, so the counts add up to the entry count.

| Outcome | Entries |
| ------- | ------: |
| partially-identified | 1,158,361 |
| identified | 93,631 |
| unresolved | 3,047 |

## Type summary

Sorted by type id. `declared` is the extension the engine registers for the type;
`from payload` is an extension the bytes themselves established. `archives` is the
exact number of archives that hold an entry of the type.

| Type | Entries | Archives | Declared | From payload | Outcomes |
| ---- | ------: | -------: | -------- | ------------ | -------- |
| 0 | 4,351 | 17 | `rpf` 4,351 | - | partially-identified 4,351 |
| 2 | 167,897 | 1,289 | `zdr` 167,897 | - | partially-identified 167,897 |
| 3 | 55,488 | 265 | `zft` 55,488 | - | partially-identified 55,488 |
| 4 | 48,584 | 179 | `zdd` 48,584 | - | partially-identified 48,584 |
| 5 | 2,612 | 33 | `ztd` 2,612 | - | partially-identified 2,612 |
| 6 | 92,199 | 970 | `zbn` 92,199 | - | partially-identified 92,199 |
| 11 | 48,612 | 422 | `zmt` 48,612 | - | identified 20,284, partially-identified 28,328 |
| 14 | 2 | 2 | `zdatb` 2 | - | unresolved 2 |
| 15 | 250,434 | 1,204 | `zbdr` 250,434 | - | partially-identified 250,434 |
| 16 | 22,382 | 132 | `zbdd` 22,382 | - | partially-identified 22,382 |
| 17 | 22,440 | 263 | `zbft` 22,440 | - | partially-identified 22,440 |
| 18 | 611 | 2 | `zvert` 611 | - | partially-identified 611 |
| 64 | 443 | 2 | `mrf` 443 | - | partially-identified 443 |
| 66 | 87 | 7 | `gfx` 87 | - | identified 87 |
| 67 | 62,384 | 384 | `zcd` 62,384 | - | partially-identified 62,384 |
| 69 | 1 | 1 | `zpmd` 1 | - | partially-identified 1 |
| 70 | 8,443 | 67 | `zpm` 8,443 | - | partially-identified 8,443 |
| 72 | 226 | 4 | `zpt` 226 | - | partially-identified 226 |
| 73 | 166,072 | 316 | `zmap` 166,072 | - | partially-identified 166,072 |
| 74 | 6,308 | 591 | `ztyp` 6,308 | - | partially-identified 6,308 |
| 77 | 3 | 1 | `zjd` 3 | - | partially-identified 3 |
| 78 | 25,608 | 131 | `zad` 25,608 | - | partially-identified 25,608 |
| 79 | 27,644 | 12 | `znv` 27,644 | - | partially-identified 27,644 |
| 86 | 11 | 1 | `zfd` 11 | - | partially-identified 11 |
| 87 | 15,067 | 185 | `zas` 15,067 | - | partially-identified 15,067 |
| 88 | 40,019 | 5 | `zsm` 40,019 | - | partially-identified 40,019 |
| 89 | 746 | 2 | `zscript` 746 | - | partially-identified 746 |
| 93 | 211 | 1 | `zfc` 211 | - | identified 211 |
| 94 | 80 | 1 | `zlfc` 80 | - | identified 80 |
| 95 | 518 | 2 | `zcg` 518 | - | partially-identified 518 |
| 96 | 1 | 1 | `zasd` 1 | - | unresolved 1 |
| 99 | 98 | 1 | `zcps` 98 | - | partially-identified 98 |
| 100 | 27,482 | 11 | `zsp` 27,482 | - | partially-identified 27,482 |
| 101 | 5 | 1 | `ztsl` 5 | - | partially-identified 5 |
| 102 | 142 | 13 | `zmmd` 142 | - | partially-identified 142 |
| 103 | 6,762 | 17 | `zfid` 6,762 | - | partially-identified 6,762 |
| 104 | 1,476 | 1 | `zmsk` 1,476 | - | unresolved 1,476 |
| 105 | 1,476 | 1 | `zhdat` 1,476 | - | unresolved 1,476 |
| 108 | 32,878 | 4 | `zascd` 32,878 | - | partially-identified 32,878 |
| 109 | 4 | 4 | `zrd` 4 | - | partially-identified 4 |
| 110 | 5 | 5 | `zsmam` 5 | - | partially-identified 5 |
| 111 | 30,511 | 39 | `zldbmt` 30,511 | - | partially-identified 30,511 |
| 113 | 2,715 | 1 | `zkit` 2,715 | - | partially-identified 2,715 |
| 114 | 518 | 2 | `zcgc` 518 | - | partially-identified 518 |
| 115 | 8,415 | 4 | `zcov` 8,415 | - | partially-identified 8,415 |
| 255 | 73,068 | 171 | - | `xml` 489 | identified 72,969, partially-identified 7, unresolved 92 |

## Distributions

### Identification kind

| Value | Entries |
| ----- | ------: |
| resource | 1,153,560 |
| format | 97,493 |
| none | 3,047 |
| xml | 491 |
| signature | 448 |

### Format

| Value | Entries |
| ----- | ------: |
| resource:segment-5 | 1,153,560 |
| format:adat | 71,676 |
| format:psin | 19,084 |
| format:rpf9 | 4,351 |
| none | 3,047 |
| format:rbf0 | 1,493 |
| format:kb2 | 797 |
| signature:Observed("move") | 443 |
| xml:CDataFileMgr__ContentChangeSetDef | 117 |
| format:gfx | 87 |
| xml:timecycle_modifier_data | 49 |
| xml:rage__bgCrackType | 36 |
| xml:CTuningFile | 34 |
| xml:CVehiclePoints | 32 |
| xml:timecycle_keyframe_data | 27 |
| xml:CDataFileMgr__ContentDef | 11 |
| xml:SSetupData | 10 |
| xml:WaveData | 6 |
| format:edup | 5 |
| xml:CDamageDataManager | 5 |
| xml:GridAtlasInfo | 4 |
| xml:CCoverProcessorTuning | 3 |
| signature:Observed("mhiu") | 2 |
| signature:Observed("sgd5") | 2 |
| xml:CVehiclePerformanceMaps | 2 |
| xml:ShoreWavePlacementData | 2 |
| xml:VehicleControlsInfo | 2 |
| xml:unvalidated | 2 |
| signature:Observed("sps1") | 1 |
| xml:ActionCoordinator__ActionCoordinatorData | 1 |
| xml:BoatHullBlackList | 1 |
| xml:CAimUpperBodyDataBlock | 1 |
| xml:CAnimSceneAttachSlotSetManager | 1 |
| xml:CAnimalAnimationContexts | 1 |
| xml:CAnimalAttackBehaviours | 1 |
| xml:CAttachmentSlotData | 1 |
| xml:CBaitingInfo | 1 |
| xml:CBodyAnimConstraintInfoStateSetManager | 1 |
| xml:CBreakableVehicleDoorLockManagerData | 1 |
| xml:CClimbTuneMgr | 1 |
| xml:CCombatInfoMgr | 1 |
| xml:CContentsOfWeatherXmlFile | 1 |
| xml:CConversationDictionary | 1 |
| xml:CConversationList | 1 |
| xml:CDiscoverableCollection | 1 |
| xml:CDoorInteractionDataList | 1 |
| xml:CDrivingStyleCollection | 1 |
| xml:CDynamicScenarioManager | 1 |
| xml:CEnergyConfigInfos | 1 |
| xml:CEntityComponentLodManagerData | 1 |
| xml:CFallenSnowData | 1 |
| xml:CFiringPatternInfoManager | 1 |
| xml:CFleeDecisionMakerData | 1 |
| xml:CFluidVesselManager | 1 |
| xml:CGarageInitDataList | 1 |
| xml:CGraphicsDefinitionsData | 1 |
| xml:CHazardNodes | 1 |
| xml:CHeadbobConditionManager | 1 |
| xml:CHealthConfigInfo | 1 |
| xml:CIdlePreferenceManager | 1 |
| xml:CLadderMetadataManager | 1 |
| xml:CLadderRailsMetadataManager | 1 |
| xml:CLassoDataManager | 1 |
| xml:CMissions | 1 |
| xml:CMoodConditionManager | 1 |
| xml:CMovieQualityVariationMap | 1 |
| xml:CObjectComponentSetManager | 1 |
| xml:CPairedPedDataBlock | 1 |
| xml:CParkingSplines | 1 |
| xml:CPedAccuracyManager | 1 |
| xml:CPedArmourMetaData | 1 |
| xml:CPedBreathingTypes | 1 |
| xml:CPedComponentSetManager | 1 |
| xml:CPedDensityScoringConfigMap | 1 |
| xml:CPedFormationInfoManager | 1 |
| xml:CPedHeadbobSettingsManager | 1 |
| xml:CPedInventoryLoadOutManager | 1 |
| xml:CPedMoodConditionTreesManager | 1 |
| xml:CPedMoodSettingsManager | 1 |
| xml:CPedMotivationInfoManager | 1 |
| xml:CPedScheduleInfoManager | 1 |
| xml:CPedSpeedDataBlock | 1 |
| xml:CPedTimeWarpSettingsManager | 1 |
| xml:CPedVariationBodyTypeManager | 1 |
| xml:CPersonaEnumValuesMap | 1 |
| xml:CPlayerDiscoverableDataCollection | 1 |
| xml:CProceduralInfo | 1 |
| xml:CScatteringTransmittance__FogVolumeListData | 1 |
| xml:CScenarioPropDataManager | 1 |
| xml:CSceneTerrainAnalyzerMgrDataInstance | 1 |
| xml:CScenicViewManager | 1 |
| xml:CSearchPointOfInterestRuleSet | 1 |
| xml:CSnowTrackData | 1 |
| xml:CStandardPosesManager | 1 |
| xml:CTVPlaylistContainer | 1 |
| xml:CTacticalAnalysisDistributionStore | 1 |
| xml:CTaskDataInfoManager | 1 |
| xml:CTaskMoveLocalMovement__Tunables | 1 |
| xml:CTrainConfigs | 1 |
| xml:CTyreDataSet | 1 |
| xml:CUpperBodyIdleConditionManager | 1 |
| xml:CUpperBodyIdleSettingsManager | 1 |
| xml:CVehicleAIHandlingEntry | 1 |
| xml:CVehicleBaseRatingsAndEstimatesMap | 1 |
| xml:CVehicleBoneOffsetsArray | 1 |
| xml:CVehicleComponentSetManager | 1 |
| xml:CVehicleDistantLightData | 1 |
| xml:CVehiclePointsMeta | 1 |
| xml:CWeaponActionHashToIndexMappings | 1 |
| xml:Clock__Filter__Presets | 1 |
| xml:Combat__GoalData__Store | 1 |
| xml:Combat__Settings__ActionStore | 1 |
| xml:Confront__StyleCollection | 1 |
| xml:CoverShadowTunables | 1 |
| xml:CustomClouds | 1 |
| xml:DiffractionProfiles | 1 |
| xml:EnvironmentalWaterDisturbManager | 1 |
| xml:FogVolumeProfileList | 1 |
| xml:GameShape__Data__LocationNameLoopkup | 1 |
| xml:GameShape__Data__ManagerSettings | 1 |
| xml:GlintsProfiles | 1 |
| xml:InteractionFoam_Tunables | 1 |
| xml:InteriorGroups | 1 |
| xml:LUTColorblindnessVariationMap | 1 |
| xml:LandingPageVideos | 1 |
| xml:LightAnimationPresets | 1 |
| xml:LostTargetSearch__Tunables | 1 |
| xml:MainWaterTune | 1 |
| xml:MapState__Data__Templates | 1 |
| xml:MaterialDataList | 1 |
| xml:Mindset__CMindsetDictionary | 1 |
| xml:ModelTagMappings | 1 |
| xml:ModelTags | 1 |
| xml:Modular__SM__AIBehaviour__LockControllerConfig | 1 |
| xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | 1 |
| xml:OceanSimPresets | 1 |
| xml:OceanWaveCalmingCurves | 1 |
| xml:PatchConstants | 1 |
| xml:PathingStyleData | 1 |
| xml:PedMotion__PedMotionData | 1 |
| xml:PostFXSpline__Store | 1 |
| xml:PromptInternal__PromptTunables | 1 |
| xml:RegionTintMap | 1 |
| xml:Relationships__GroupsData | 1 |
| xml:Respawn__MetaData | 1 |
| xml:RumbleProfileList | 1 |
| xml:SMandatoryPacksData | 1 |
| xml:STPedMotionPredictionSetContainer | 1 |
| xml:STPedNavigationPredictiontPresetContainer | 1 |
| xml:STS_Config | 1 |
| xml:SoftBoundTuningList | 1 |
| xml:SpecialAbilityTagTargetsSettings | 1 |
| xml:Sprinklers__RootData | 1 |
| xml:StudioConfigurationData | 1 |
| xml:Tactical__PointValidation__DataStore | 1 |
| xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | 1 |
| xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | 1 |
| xml:TextureGridInfo | 1 |
| xml:TyreProfileList | 1 |
| xml:VehicleFragImpulseFunction | 1 |
| xml:WalkAndTalkProfileData | 1 |
| xml:WaterTessellationSettings__AllAllowancesAndThresholds | 1 |
| xml:WeaponAnimations__ConfigData | 1 |
| xml:WeaponAnimations__FullbodyControllerData | 1 |
| xml:Witnesses__Informations | 1 |
| xml:aiNavIMapGroupData | 1 |
| xml:hrsSimTuneMgr | 1 |
| xml:naSpeechEventTypeBatchRequestParams | 1 |
| xml:rage__MediaDecoderSettings | 1 |
| xml:rage__bgConfig | 1 |
| xml:rage__crRetarget__SolversTunables | 1 |
| xml:rage__fragTuneStruct | 1 |
| xml:rage__fwRetargetCoordinatorConfig | 1 |
| xml:rage__phMBS_MaterialParamsDatabase_Def | 1 |
| xml:sCollisionEventScannerTuning | 1 |
| xml:sPedDamageModifiers | 1 |
| xml:sPedDistractionModifiers | 1 |
| xml:time_data | 1 |

### Capability

| Value | Entries |
| ----- | ------: |
| resource | 1,153,560 |
| structural | 93,142 |
| archive | 4,351 |
| bytes | 3,495 |
| text | 491 |

### Outcome

| Value | Entries |
| ----- | ------: |
| partially-identified | 1,158,361 |
| identified | 93,631 |
| unresolved | 3,047 |

### Extension

| Value | Entries |
| ----- | ------: |
| zbdr | 250,434 |
| zdr | 167,897 |
| zmap | 166,072 |
| zbn | 92,199 |
| - | 72,579 |
| zcd | 62,384 |
| zft | 55,488 |
| zmt | 48,612 |
| zdd | 48,584 |
| zsm | 40,019 |
| zascd | 32,878 |
| zldbmt | 30,511 |
| znv | 27,644 |
| zsp | 27,482 |
| zad | 25,608 |
| zbft | 22,440 |
| zbdd | 22,382 |
| zas | 15,067 |
| zpm | 8,443 |
| zcov | 8,415 |
| zfid | 6,762 |
| ztyp | 6,308 |
| rpf | 4,351 |
| zkit | 2,715 |
| ztd | 2,612 |
| zhdat | 1,476 |
| zmsk | 1,476 |
| zscript | 746 |
| zvert | 611 |
| zcg | 518 |
| zcgc | 518 |
| xml | 489 |
| mrf | 443 |
| zpt | 226 |
| zfc | 211 |
| zmmd | 142 |
| zcps | 98 |
| gfx | 87 |
| zlfc | 80 |
| zfd | 11 |
| zsmam | 5 |
| ztsl | 5 |
| zrd | 4 |
| zjd | 3 |
| zdatb | 2 |
| zasd | 1 |
| zpmd | 1 |

### Extension provenance

| Value | Entries |
| ----- | ------: |
| native | 1,181,971 |
| unresolved | 72,579 |
| payload | 489 |

### Structure claim

| Value | Entries |
| ----- | ------: |
| unknown | 1,157,055 |
| verified | 93,631 |
| probable | 4,351 |
| tentative | 2 |

### Payload state

| Value | Entries |
| ----- | ------: |
| decoded | 1,255,039 |

### Storage

| Value | Entries |
| ----- | ------: |
| chunked-2 | 1,139,128 |
| stored | 76,826 |
| chunked-3 | 24,436 |
| chunked-4 | 14,488 |
| raw-deflate | 161 |

### Entry type

| Value | Entries |
| ----- | ------: |
| 15 | 250,434 |
| 2 | 167,897 |
| 73 | 166,072 |
| 6 | 92,199 |
| 255 | 73,068 |
| 67 | 62,384 |
| 3 | 55,488 |
| 11 | 48,612 |
| 4 | 48,584 |
| 88 | 40,019 |
| 108 | 32,878 |
| 111 | 30,511 |
| 79 | 27,644 |
| 100 | 27,482 |
| 78 | 25,608 |
| 17 | 22,440 |
| 16 | 22,382 |
| 87 | 15,067 |
| 70 | 8,443 |
| 115 | 8,415 |
| 103 | 6,762 |
| 74 | 6,308 |
| 0 | 4,351 |
| 113 | 2,715 |
| 5 | 2,612 |
| 104 | 1,476 |
| 105 | 1,476 |
| 89 | 746 |
| 18 | 611 |
| 114 | 518 |
| 95 | 518 |
| 64 | 443 |
| 72 | 226 |
| 93 | 211 |
| 102 | 142 |
| 99 | 98 |
| 66 | 87 |
| 94 | 80 |
| 86 | 11 |
| 101 | 5 |
| 110 | 5 |
| 109 | 4 |
| 77 | 3 |
| 14 | 2 |
| 69 | 1 |
| 96 | 1 |

## Every combination

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 0 | format:rpf9 | format:rpf9 | stored | no | decoded | probable | archive | rpf | 4351 | 17 |
| 2 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zdr | 164701 | 1532 |
| 2 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-4 | no | decoded | unknown | resource | zdr | 3196 | 3 |
| 3 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zft | 55488 | 320 |
| 4 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zdd | 48328 | 178 |
| 4 | resource:segment-5 | resource:s5:zero+small | chunked-4 | no | decoded | unknown | resource | zdd | 256 | 1 |
| 5 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | ztd | 2612 | 33 |
| 6 | resource:segment-5 | resource:s5:small+zero | chunked-2 | no | decoded | unknown | resource | zbn | 90545 | 969 |
| 6 | resource:segment-5 | resource:s5:small+zero | chunked-4 | no | decoded | unknown | resource | zbn | 1654 | 1 |
| 11 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zmt | 28295 | 202 |
| 11 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zmt | 18294 | 282 |
| 11 | format:rbf0 | format:rbf0 | chunked-3 | no | decoded | verified | structural | zmt | 1278 | 10 |
| 11 | format:psin | format:psin | chunked-3 | yes | decoded | verified | structural | zmt | 437 | 10 |
| 11 | format:rbf0 | format:rbf0 | raw-deflate | no | decoded | verified | structural | zmt | 156 | 1 |
| 11 | format:rbf0 | format:rbf0 | chunked-3 | yes | decoded | verified | structural | zmt | 59 | 5 |
| 11 | format:psin | format:psin | chunked-4 | no | decoded | verified | structural | zmt | 55 | 1 |
| 11 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | zmt | 33 | 1 |
| 11 | format:psin | format:psin | raw-deflate | yes | decoded | verified | structural | zmt | 4 | 4 |
| 11 | format:psin | format:psin | raw-deflate | no | decoded | verified | structural | zmt | 1 | 1 |
| 14 | none | binary:30030100 | chunked-3 | no | decoded | unknown | bytes | zdatb | 1 | 1 |
| 14 | none | binary:58340400 | chunked-3 | yes | decoded | unknown | bytes | zdatb | 1 | 1 |
| 15 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zbdr | 245666 | 1203 |
| 15 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-4 | no | decoded | unknown | resource | zbdr | 4768 | 1 |
| 16 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zbdd | 22126 | 131 |
| 16 | resource:segment-5 | resource:s5:zero+small | chunked-4 | no | decoded | unknown | resource | zbdd | 256 | 1 |
| 17 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zbft | 22440 | 263 |
| 18 | resource:segment-5 | resource:s5:other+other | chunked-2 | no | decoded | unknown | resource | zvert | 611 | 4 |
| 64 | signature:Observed("move") | signature:Observed("move") | chunked-3 | no | decoded | unknown | bytes | mrf | 443 | 2 |
| 66 | format:gfx | format:gfx | chunked-3 | no | decoded | verified | structural | gfx | 87 | 7 |
| 67 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zcd | 62375 | 383 |
| 67 | resource:segment-5 | resource:s5:zero+zero | chunked-4 | no | decoded | unknown | resource | zcd | 9 | 1 |
| 69 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zpmd | 1 | 1 |
| 70 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zpm | 8443 | 67 |
| 72 | resource:segment-5 | resource:s5:other+zero | chunked-2 | no | decoded | unknown | resource | zpt | 226 | 13 |
| 73 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zmap | 161985 | 312 |
| 73 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | zmap | 4087 | 4 |
| 74 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | ztyp | 6135 | 589 |
| 74 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | ztyp | 173 | 2 |
| 77 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zjd | 3 | 1 |
| 78 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zad | 25608 | 131 |
| 79 | resource:segment-5 | resource:s5:small+zero | chunked-2 | no | decoded | unknown | resource | znv | 27644 | 12 |
| 86 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zfd | 11 | 1 |
| 87 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zas | 15067 | 185 |
| 88 | resource:segment-5 | resource:s5:zero+other | chunked-2 | no | decoded | unknown | resource | zsm | 40019 | 10 |
| 89 | resource:segment-5 | resource:s5:other+small | chunked-2 | yes | decoded | unknown | resource | zscript | 746 | 11 |
| 93 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zfc | 211 | 1 |
| 94 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zlfc | 80 | 1 |
| 95 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zcg | 518 | 2 |
| 96 | none | zeros | chunked-3 | no | decoded | unknown | bytes | zasd | 1 | 1 |
| 99 | resource:segment-5 | resource:s5:other+small | chunked-2 | no | decoded | unknown | resource | zcps | 98 | 4 |
| 100 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zsp | 27482 | 11 |
| 101 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | ztsl | 5 | 1 |
| 102 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zmmd | 142 | 13 |
| 103 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zfid | 6762 | 17 |
| 104 | none | binary:01000102 | chunked-3 | no | decoded | unknown | bytes | zmsk | 1476 | 1 |
| 105 | none | binary:50414d48 | chunked-3 | no | decoded | unknown | bytes | zhdat | 1476 | 1 |
| 108 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zascd | 32878 | 4 |
| 109 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zrd | 4 | 4 |
| 110 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zsmam | 5 | 5 |
| 111 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zldbmt | 30511 | 39 |
| 113 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zkit | 2715 | 1 |
| 114 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zcgc | 518 | 3 |
| 115 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zcov | 8415 | 4 |
| 255 | format:adat | format:adat | stored | no | decoded | verified | structural | - | 71676 | 122 |
| 255 | format:kb2 | format:kb2 | stored | no | decoded | verified | structural | - | 797 | 4 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | no | decoded | verified | text | xml | 96 | 10 |
| 255 | none | binary:12000000 | chunked-3 | no | decoded | unknown | bytes | - | 82 | 67 |
| 255 | xml:timecycle_modifier_data | xml:timecycle_modifier_data | chunked-3 | no | decoded | verified | text | xml | 49 | 1 |
| 255 | xml:rage__bgCrackType | xml:rage__bgCrackType | chunked-3 | yes | decoded | verified | text | xml | 36 | 1 |
| 255 | xml:CVehiclePoints | xml:CVehiclePoints | chunked-3 | no | decoded | verified | text | xml | 32 | 1 |
| 255 | xml:timecycle_keyframe_data | xml:timecycle_keyframe_data | chunked-3 | no | decoded | verified | text | xml | 27 | 1 |
| 255 | xml:CTuningFile | xml:CTuningFile | chunked-3 | yes | decoded | verified | text | xml | 24 | 1 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | yes | decoded | verified | text | xml | 21 | 1 |
| 255 | xml:CDataFileMgr__ContentDef | xml:CDataFileMgr__ContentDef | chunked-3 | no | decoded | verified | text | xml | 11 | 10 |
| 255 | xml:CTuningFile | xml:CTuningFile | chunked-3 | no | decoded | verified | text | xml | 10 | 1 |
| 255 | xml:SSetupData | xml:SSetupData | chunked-3 | no | decoded | verified | text | xml | 10 | 10 |
| 255 | none | text | chunked-3 | yes | decoded | unknown | bytes | - | 9 | 1 |
| 255 | xml:WaveData | xml:WaveData | chunked-3 | yes | decoded | verified | text | xml | 6 | 1 |
| 255 | format:edup | format:edup | chunked-3 | no | decoded | verified | structural | - | 5 | 5 |
| 255 | xml:CDamageDataManager | xml:CDamageDataManager | chunked-3 | no | decoded | verified | text | xml | 5 | 1 |
| 255 | xml:GridAtlasInfo | xml:GridAtlasInfo | chunked-3 | no | decoded | verified | text | xml | 4 | 1 |
| 255 | xml:CCoverProcessorTuning | xml:CCoverProcessorTuning | chunked-3 | no | decoded | verified | text | xml | 3 | 1 |
| 255 | format:psin | format:psin | chunked-3 | yes | decoded | verified | structural | - | 2 | 1 |
| 255 | signature:Observed("mhiu") | signature:Observed("mhiu") | chunked-3 | no | decoded | unknown | bytes | - | 2 | 1 |
| 255 | signature:Observed("sgd5") | signature:Observed("sgd5") | stored | no | decoded | unknown | bytes | - | 2 | 1 |
| 255 | xml:CVehiclePerformanceMaps | xml:CVehiclePerformanceMaps | chunked-3 | no | decoded | verified | text | xml | 2 | 1 |
| 255 | xml:ShoreWavePlacementData | xml:ShoreWavePlacementData | chunked-3 | no | decoded | verified | text | xml | 2 | 2 |
| 255 | xml:VehicleControlsInfo | xml:VehicleControlsInfo | chunked-3 | yes | decoded | verified | text | xml | 2 | 1 |
| 255 | xml:unvalidated | xml:unvalidated | chunked-3 | no | decoded | tentative | text | - | 2 | 1 |
| 255 | none | text | chunked-4 | no | decoded | unknown | bytes | - | 1 | 1 |
| 255 | signature:Observed("sps1") | signature:Observed("sps1") | chunked-3 | no | decoded | unknown | bytes | - | 1 | 1 |
| 255 | xml:ActionCoordinator__ActionCoordinatorData | xml:ActionCoordinator__ActionCoordinatorData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:BoatHullBlackList | xml:BoatHullBlackList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAimUpperBodyDataBlock | xml:CAimUpperBodyDataBlock | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimSceneAttachSlotSetManager | xml:CAnimSceneAttachSlotSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimalAnimationContexts | xml:CAnimalAnimationContexts | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimalAttackBehaviours | xml:CAnimalAttackBehaviours | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAttachmentSlotData | xml:CAttachmentSlotData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBaitingInfo | xml:CBaitingInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBodyAnimConstraintInfoStateSetManager | xml:CBodyAnimConstraintInfoStateSetManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBreakableVehicleDoorLockManagerData | xml:CBreakableVehicleDoorLockManagerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CClimbTuneMgr | xml:CClimbTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CCombatInfoMgr | xml:CCombatInfoMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CContentsOfWeatherXmlFile | xml:CContentsOfWeatherXmlFile | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CConversationDictionary | xml:CConversationDictionary | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CConversationList | xml:CConversationList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDiscoverableCollection | xml:CDiscoverableCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDoorInteractionDataList | xml:CDoorInteractionDataList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDrivingStyleCollection | xml:CDrivingStyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDynamicScenarioManager | xml:CDynamicScenarioManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CEnergyConfigInfos | xml:CEnergyConfigInfos | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CEntityComponentLodManagerData | xml:CEntityComponentLodManagerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFallenSnowData | xml:CFallenSnowData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFiringPatternInfoManager | xml:CFiringPatternInfoManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFleeDecisionMakerData | xml:CFleeDecisionMakerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFluidVesselManager | xml:CFluidVesselManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CGarageInitDataList | xml:CGarageInitDataList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CGraphicsDefinitionsData | xml:CGraphicsDefinitionsData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHazardNodes | xml:CHazardNodes | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHeadbobConditionManager | xml:CHeadbobConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHealthConfigInfo | xml:CHealthConfigInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CIdlePreferenceManager | xml:CIdlePreferenceManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLadderMetadataManager | xml:CLadderMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLadderRailsMetadataManager | xml:CLadderRailsMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLassoDataManager | xml:CLassoDataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMissions | xml:CMissions | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMoodConditionManager | xml:CMoodConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMovieQualityVariationMap | xml:CMovieQualityVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CObjectComponentSetManager | xml:CObjectComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPairedPedDataBlock | xml:CPairedPedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CParkingSplines | xml:CParkingSplines | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedAccuracyManager | xml:CPedAccuracyManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedArmourMetaData | xml:CPedArmourMetaData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedBreathingTypes | xml:CPedBreathingTypes | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedComponentSetManager | xml:CPedComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedDensityScoringConfigMap | xml:CPedDensityScoringConfigMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedFormationInfoManager | xml:CPedFormationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedHeadbobSettingsManager | xml:CPedHeadbobSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedInventoryLoadOutManager | xml:CPedInventoryLoadOutManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMoodConditionTreesManager | xml:CPedMoodConditionTreesManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMoodSettingsManager | xml:CPedMoodSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMotivationInfoManager | xml:CPedMotivationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedScheduleInfoManager | xml:CPedScheduleInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedSpeedDataBlock | xml:CPedSpeedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedTimeWarpSettingsManager | xml:CPedTimeWarpSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedVariationBodyTypeManager | xml:CPedVariationBodyTypeManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPersonaEnumValuesMap | xml:CPersonaEnumValuesMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPlayerDiscoverableDataCollection | xml:CPlayerDiscoverableDataCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CProceduralInfo | xml:CProceduralInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScatteringTransmittance__FogVolumeListData | xml:CScatteringTransmittance__FogVolumeListData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScenarioPropDataManager | xml:CScenarioPropDataManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSceneTerrainAnalyzerMgrDataInstance | xml:CSceneTerrainAnalyzerMgrDataInstance | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScenicViewManager | xml:CScenicViewManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSearchPointOfInterestRuleSet | xml:CSearchPointOfInterestRuleSet | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSnowTrackData | xml:CSnowTrackData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CStandardPosesManager | xml:CStandardPosesManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTVPlaylistContainer | xml:CTVPlaylistContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTacticalAnalysisDistributionStore | xml:CTacticalAnalysisDistributionStore | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTaskDataInfoManager | xml:CTaskDataInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTaskMoveLocalMovement__Tunables | xml:CTaskMoveLocalMovement__Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTrainConfigs | xml:CTrainConfigs | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTyreDataSet | xml:CTyreDataSet | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CUpperBodyIdleConditionManager | xml:CUpperBodyIdleConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CUpperBodyIdleSettingsManager | xml:CUpperBodyIdleSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleAIHandlingEntry | xml:CVehicleAIHandlingEntry | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleBaseRatingsAndEstimatesMap | xml:CVehicleBaseRatingsAndEstimatesMap | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleBoneOffsetsArray | xml:CVehicleBoneOffsetsArray | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleComponentSetManager | xml:CVehicleComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleDistantLightData | xml:CVehicleDistantLightData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehiclePointsMeta | xml:CVehiclePointsMeta | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CWeaponActionHashToIndexMappings | xml:CWeaponActionHashToIndexMappings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Clock__Filter__Presets | xml:Clock__Filter__Presets | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Combat__GoalData__Store | xml:Combat__GoalData__Store | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Combat__Settings__ActionStore | xml:Combat__Settings__ActionStore | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Confront__StyleCollection | xml:Confront__StyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CoverShadowTunables | xml:CoverShadowTunables | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CustomClouds | xml:CustomClouds | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:DiffractionProfiles | xml:DiffractionProfiles | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:EnvironmentalWaterDisturbManager | xml:EnvironmentalWaterDisturbManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:FogVolumeProfileList | xml:FogVolumeProfileList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GameShape__Data__LocationNameLoopkup | xml:GameShape__Data__LocationNameLoopkup | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GameShape__Data__ManagerSettings | xml:GameShape__Data__ManagerSettings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GlintsProfiles | xml:GlintsProfiles | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:InteractionFoam_Tunables | xml:InteractionFoam_Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:InteriorGroups | xml:InteriorGroups | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LUTColorblindnessVariationMap | xml:LUTColorblindnessVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LandingPageVideos | xml:LandingPageVideos | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LightAnimationPresets | xml:LightAnimationPresets | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LostTargetSearch__Tunables | xml:LostTargetSearch__Tunables | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MainWaterTune | xml:MainWaterTune | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MapState__Data__Templates | xml:MapState__Data__Templates | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MaterialDataList | xml:MaterialDataList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Mindset__CMindsetDictionary | xml:Mindset__CMindsetDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:ModelTagMappings | xml:ModelTagMappings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:ModelTags | xml:ModelTags | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Modular__SM__AIBehaviour__LockControllerConfig | xml:Modular__SM__AIBehaviour__LockControllerConfig | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:OceanSimPresets | xml:OceanSimPresets | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:OceanWaveCalmingCurves | xml:OceanWaveCalmingCurves | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PatchConstants | xml:PatchConstants | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PathingStyleData | xml:PathingStyleData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PedMotion__PedMotionData | xml:PedMotion__PedMotionData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PostFXSpline__Store | xml:PostFXSpline__Store | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PromptInternal__PromptTunables | xml:PromptInternal__PromptTunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:RegionTintMap | xml:RegionTintMap | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Relationships__GroupsData | xml:Relationships__GroupsData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Respawn__MetaData | xml:Respawn__MetaData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:RumbleProfileList | xml:RumbleProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SMandatoryPacksData | xml:SMandatoryPacksData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STPedMotionPredictionSetContainer | xml:STPedMotionPredictionSetContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STPedNavigationPredictiontPresetContainer | xml:STPedNavigationPredictiontPresetContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STS_Config | xml:STS_Config | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SoftBoundTuningList | xml:SoftBoundTuningList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SpecialAbilityTagTargetsSettings | xml:SpecialAbilityTagTargetsSettings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Sprinklers__RootData | xml:Sprinklers__RootData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:StudioConfigurationData | xml:StudioConfigurationData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Tactical__PointValidation__DataStore | xml:Tactical__PointValidation__DataStore | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TextureGridInfo | xml:TextureGridInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TyreProfileList | xml:TyreProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:VehicleFragImpulseFunction | xml:VehicleFragImpulseFunction | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WalkAndTalkProfileData | xml:WalkAndTalkProfileData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WaterTessellationSettings__AllAllowancesAndThresholds | xml:WaterTessellationSettings__AllAllowancesAndThresholds | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WeaponAnimations__ConfigData | xml:WeaponAnimations__ConfigData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WeaponAnimations__FullbodyControllerData | xml:WeaponAnimations__FullbodyControllerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Witnesses__Informations | xml:Witnesses__Informations | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:aiNavIMapGroupData | xml:aiNavIMapGroupData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:hrsSimTuneMgr | xml:hrsSimTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:naSpeechEventTypeBatchRequestParams | xml:naSpeechEventTypeBatchRequestParams | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__MediaDecoderSettings | xml:rage__MediaDecoderSettings | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__bgConfig | xml:rage__bgConfig | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__crRetarget__SolversTunables | xml:rage__crRetarget__SolversTunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__fragTuneStruct | xml:rage__fragTuneStruct | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__fwRetargetCoordinatorConfig | xml:rage__fwRetargetCoordinatorConfig | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__phMBS_MaterialParamsDatabase_Def | xml:rage__phMBS_MaterialParamsDatabase_Def | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sCollisionEventScannerTuning | xml:sCollisionEventScannerTuning | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sPedDamageModifiers | xml:sPedDamageModifiers | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sPedDistractionModifiers | xml:sPedDistractionModifiers | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:time_data | xml:time_data | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |

## By entry type

### Type 0: 4351 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 0 | format:rpf9 | format:rpf9 | stored | no | decoded | probable | archive | rpf | 4351 | 17 |

Samples of type 0 as `format:rpf9`:
- `anim.rpf!0`: 6,912 bytes, head `39465052c00200009002000010010000eea950ee299baea7007a040050010000`
- `anim.rpf!1`: 858,672 bytes, head `39465052800d0000000c0000300a000049e5e4d63ebd6f79007a040050010000`
- `anim.rpf!2`: 151,120 bytes, head `39465052200b000080070000502e00003fec8c787656199b007a040050010000`
- `audio.rpf!0`: 143,174,144 bytes, head `39465052400f0000c00c0000e00800005b25daca02127b1d007a040050010000`
- `audio.rpf!1`: 24,091,424 bytes, head `3946505240040000d0030000e00000004266f4a1dd304898007a040050010000`
- `audio.rpf!2`: 149,246,944 bytes, head `39465052702a0000e0220000e01300002866a00d7c7c82c9007a040050010000`
- `data.rpf!0`: 414,544 bytes, head `39465052601f0000e019000050130000a780d08a7cbbad5c007a040050010000`
- `data.rpf!1`: 1,110,576 bytes, head `3946505200050000b00400008000000077f82a03f3586e1a007a040050010000`
- `data.rpf!2`: 11,187,360 bytes, head `39465052b033010060ff0000a07400005bb94d338a2ec14b007a040050010000`
- `levels.rpf!0`: 95,040 bytes, head `394650524003000000030000400000006bee5475bec1d328007a040050010000`
- `levels.rpf!1`: 8,256 bytes, head `394650528002000070020000400000009925831bb44c0e96007a040050010000`
- `levels.rpf!2`: 51,497,440 bytes, head `39465052d09a000070890000e0b900000293974b4ab21c37007a050030220000`
- `navmeshes.rpf!0`: 902,933,600 bytes, head `39465052709c0200c03c020060ac0000159858639a8ee279007a040050010000`
- `navmeshes.rpf!1`: 64,889,056 bytes, head `39465052e0c10200904c0200e0f001004442e493d15eec9c007a040050010000`
- `navmeshes.rpf!2`: 10,304,608 bytes, head `39465052a0660200f006020060ac000042ecb357c6261e64007a040050010000`
- `pack/core_bvh4/core_bvh4.rpf!0`: 707,456 bytes, head `39465052f00c0000600b0000e003000036830e76a524e4df007a040050010000`
- `pack/core_bvh4/core_bvh4.rpf!1`: 7,211,536 bytes, head `3946505210120000d00f0000e003000017bf70faa40dc26b007a040050010000`
- `pack/core_bvh4/core_bvh4.rpf!2`: 9,253,920 bytes, head `39465052409e01005060010020a400003e942ca369507bbe007a040050010000`
- `pack/core_licenses/core_licenses_data.rpf!0`: 7,760 bytes, head `394650522003000000030000500000003ebc6832fd091054007a040050010000`
- `pack/core_restofworld/core_restofworld.rpf!0`: 41,360 bytes, head `39465052b002000090020000500000004104a8ef7ca75efc007a040050010000`
- `pack/core_restofworld/core_restofworld.rpf!1`: 912 bytes, head `39465052c0020000a002000070000000a3fe64d1c37c2b16007a040050010000`
- `pack/core_restofworld/core_restofworld.rpf!2`: 22,363,648 bytes, head `39465052a028010060090100004e0000db91e02f645f323b007a040050010000`
- `pack/core_restofworld001/core_restofworld001.rpf!0`: 785,200 bytes, head `39465052b0070000e0060000500600006506a274ec5ac1a9007a040050010000`
- `pack/shared_minigame000/shared_minigame000.rpf!0`: 79,584 bytes, head `3946505230040000e0030000b00000001f00f294c6dbb731007a040050010000`

### Type 2: 167897 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 2 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zdr | 164701 | 1532 |
| 2 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-4 | no | decoded | unknown | resource | zdr | 3196 | 3 |

Samples of type 2 as `resource:s5:ptr:seg5+ptr:seg5`:
- `data.rpf!26!2`: 7,984 bytes, head `00000000000000005014005000000000d012005000000000800e005000000000`
- `data.rpf!26!3`: 62,464 bytes, head `0000000000000000600e005000000000d00c0050000000008007005000000000`
- `data.rpf!26!6`: 36,688 bytes, head `0000000000000000d0140050000000009012005000000000c00c005000000000`
- `data.rpf!14!0`: 42,752 bytes, head `0000000000000000b080005000000000c07c0050000000000000000000000000`
- `data.rpf!14!1`: 822,080 bytes, head `0000000000000000e08809500000000030870950000000000000000000000000`
- `data.rpf!14!2`: 543,408 bytes, head `0000000000000000e02b07500000000030280750000000000000000000000000`
- `levels.rpf!5!6`: 221,296 bytes, head `00000000000000008036005000000000a033005000000000f01d005000000000`
- `levels.rpf!5!70`: 36,416 bytes, head `0000000000000000501c005000000000e019005000000000b012005000000000`
- `levels.rpf!5!72`: 84,592 bytes, head `0000000000000000d03600500000000050340050000000001022005000000000`
- `levels.rpf!2!0`: 1,603,856 bytes, head `0000000000000000c070045000000000005a0450000000000000000000000000`
- `levels.rpf!2!2`: 354,048 bytes, head `0000000000000000307600500000000080740050000000000000000000000000`
- `levels.rpf!2!3`: 945,120 bytes, head `000000000000000090da01500000000010d50150000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!33`: 40,720 bytes, head `0000000000000000b02a00500000000040260050000000007016005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!43`: 42,880 bytes, head `0000000000000000e029005000000000a025005000000000901a005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!82`: 55,696 bytes, head `0000000000000000301a0050000000006016005000000000100d005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!0`: 11,040 bytes, head `0000000000000000a01a005000000000b0170050000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!2`: 2,981,792 bytes, head `000000000000000080b900500000000040b50050000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!6`: 68,816 bytes, head `00000000000000004033005000000000f02e0050000000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!29!111`: 82,256 bytes, head `0000000000000000000d005000000000100c005000000000b007005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!29!174`: 1,019,168 bytes, head `0000000000000000008a0050000000000087005000000000207c005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!29!179`: 314,624 bytes, head `00000000000000004015005000000000d013005000000000c00a005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!2`: 18,976 bytes, head `0000000000000000b02f005000000000802d0050000000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!3`: 2,816 bytes, head `0000000000000000500800500000000030070050000000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!4`: 407,376 bytes, head `0000000000000000d0ff005000000000c0620150000000000000000000000000`

Samples of type 2 as `resource:s5:ptr:seg5+ptr:seg5`:
- `levels.rpf!1719!31`: 24,272 bytes, head `0000000000000000e00f005000000000d00d0050000000004008005000000000`
- `levels.rpf!1719!90`: 62,704 bytes, head `0000000000000000d015005000000000f012005000000000300c005000000000`
- `levels.rpf!1719!107`: 21,472 bytes, head `0000000000000000e00f005000000000d00d0050000000004008005000000000`
- `levels.rpf!1719!4`: 54,928 bytes, head `00000000000000006055005000000000b04f0050000000000000000000000000`
- `levels.rpf!1719!5`: 5,376 bytes, head `0000000000000000b00d005000000000900c0050000000000000000000000000`
- `levels.rpf!1719!6`: 4,992 bytes, head `0000000000000000000e005000000000e00c0050000000000000000000000000`

### Type 3: 55488 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 3 | resource:segment-5 | resource:s5:ptr:seg5+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zft | 55488 | 320 |

Samples of type 3 as `resource:s5:ptr:seg5+ptr:seg5`:
- `data.rpf!26!0`: 55,712 bytes, head `0000000000000000001400500000000050080050000000005002005000000000`
- `data.rpf!26!1`: 19,392 bytes, head `0000000000000000701700500000000040090050000000005002005000000000`
- `data.rpf!26!4`: 68,512 bytes, head `0000000000000000c01400500000000050070050000000005002005000000000`
- `levels.rpf!5!0`: 11,456 bytes, head `0000000000000000d017005000000000e00a005000000000b006005000000000`
- `levels.rpf!5!1`: 75,344 bytes, head `00000000000000005039005000000000901f0050000000009018005000000000`
- `levels.rpf!5!2`: 69,776 bytes, head `00000000000000001044005000000000c022005000000000901e005000000000`
- `levels.rpf!12!8`: 63,616 bytes, head `0000000000000000a0240050000000000000000000000000500e005000000000`
- `levels.rpf!12!9`: 9,072 bytes, head `0000000000000000a0150050000000000000000000000000b007005000000000`
- `levels.rpf!12!20`: 137,296 bytes, head `000000000000000020150050000000000000000000000000b007005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!1`: 2,164,624 bytes, head `000000000000000080770050000000003050005000000000003d005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!3`: 161,248 bytes, head `0000000000000000e036005000000000a02c005000000000c027005000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!4`: 51,328 bytes, head `0000000000000000702b005000000000a0150050000000007011005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!33!10`: 9,840 bytes, head `00000000000000006019005000000000800e0050000000008007005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!33!32`: 350,528 bytes, head `0000000000000000b096005000000000f05c005000000000f055005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!33!45`: 324,800 bytes, head `000000000000000050ab005000000000e06a005000000000e063005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!33!94`: 192,720 bytes, head `0000000000000000601d0050000000000000000000000000d00e005000000000`
- `packs.rpf!18!0`: 23,120 bytes, head `0000000000000000a054005000000000b03f005000000000a03d005000000000`
- `packs.rpf!18!1`: 10,464 bytes, head `0000000000000000b023005000000000e018005000000000c014005000000000`
- `packs.rpf!18!2`: 25,200 bytes, head `0000000000000000d05c00500000000090470050000000006041005000000000`

### Type 4: 48584 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 4 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zdd | 48328 | 178 |
| 4 | resource:segment-5 | resource:s5:zero+small | chunked-4 | no | decoded | unknown | resource | zdd | 256 | 1 |

Samples of type 4 as `resource:s5:zero+small`:
- `data.rpf!7!0`: 811,456 bytes, head `0000000000000000705f00500000000000000000000000000100000000000000`
- `data.rpf!7!1`: 4,576 bytes, head `0000000000000000700500500000000000000000000000000100000000000000`
- `data.rpf!7!2`: 176,672 bytes, head `0000000000000000e00400500000000000000000000000000100000000000000`
- `levels.rpf!14!12`: 934,768 bytes, head `0000000000000000505501500000000000000000000000000100000000000000`
- `levels.rpf!14!25`: 5,328 bytes, head `0000000000000000200e00500000000000000000000000000100000000000000`
- `levels.rpf!14!194`: 4,480 bytes, head `0000000000000000f00d00500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!2!0`: 8,640 bytes, head `0000000000000000500b00500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!2!1`: 212,688 bytes, head `0000000000000000703900500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!2!2`: 160,224 bytes, head `0000000000000000006900500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!1`: 122,624 bytes, head `0000000000000000002000500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!5`: 9,568 bytes, head `0000000000000000e01000500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!20`: 3,056 bytes, head `0000000000000000900800500000000000000000000000000100000000000000`
- `pack/story000/story000.rpf!131!0`: 28,512 bytes, head `0000000000000000801b00500000000000000000000000000100000000000000`
- `pack/story000/story000.rpf!131!1`: 28,736 bytes, head `0000000000000000801b00500000000000000000000000000100000000000000`
- `pack/story000/story000.rpf!131!2`: 22,944 bytes, head `0000000000000000801b00500000000000000000000000000100000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!17!0`: 67,088 bytes, head `0000000000000000f01c00500000000000000000000000000100000000000000`
- `packs.rpf!7!0`: 344,144 bytes, head `0000000000000000301300500000000000000000000000000100000000000000`
- `packs.rpf!7!1`: 792,096 bytes, head `0000000000000000f01300500000000000000000000000000100000000000000`
- `packs.rpf!7!2`: 716,192 bytes, head `0000000000000000200e00500000000000000000000000000100000000000000`

Samples of type 4 as `resource:s5:zero+small`:
- `levels.rpf!1719!7`: 436,656 bytes, head `000000000000000000ad00500000000000000000000000000100000000000000`
- `levels.rpf!1719!12`: 19,184 bytes, head `0000000000000000502900500000000000000000000000000100000000000000`
- `levels.rpf!1719!25`: 11,504 bytes, head `0000000000000000c01000500000000000000000000000000100000000000000`

### Type 5: 2612 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 5 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | ztd | 2612 | 33 |

Samples of type 5 as `resource:s5:zero+small`:
- `data.rpf!1!0`: 95,104 bytes, head `0000000000000000700200500000000000000000000000000100000000000000`
- `data.rpf!1!1`: 84,224 bytes, head `0000000000000000100700500000000000000000000000000100000000000000`
- `data.rpf!1!2`: 197,008 bytes, head `0000000000000000200100500000000000000000000000000100000000000000`
- `levels.rpf!637!0`: 524,544 bytes, head `0000000000000000b00000500000000000000000000000000100000000000000`
- `levels.rpf!637!1`: 524,544 bytes, head `0000000000000000b00000500000000000000000000000000100000000000000`
- `levels.rpf!637!2`: 524,544 bytes, head `0000000000000000b00000500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!4!0`: 8,624 bytes, head `0000000000000000700100500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!4!1`: 8,624 bytes, head `0000000000000000700100500000000000000000000000000100000000000000`
- `pack/core_restofworld/core_restofworld.rpf!4!2`: 4,368 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!11!0`: 2,162,960 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!11!1`: 262,416 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!11!2`: 262,416 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `textures.rpf!0!0`: 2,557,072 bytes, head `0000000000000000900300500000000000000000000000000100000000000000`
- `textures.rpf!1!0`: 51,040 bytes, head `0000000000000000100600500000000000000000000000000100000000000000`
- `textures.rpf!2!0`: 721,152 bytes, head `0000000000000000b00000500000000000000000000000000100000000000000`

### Type 6: 92199 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 6 | resource:segment-5 | resource:s5:small+zero | chunked-2 | no | decoded | unknown | resource | zbn | 90545 | 969 |
| 6 | resource:segment-5 | resource:s5:small+zero | chunked-4 | no | decoded | unknown | resource | zbn | 1654 | 1 |

Samples of type 6 as `resource:s5:small+zero`:
- `levels.rpf!2!1`: 73,872 bytes, head `000000000000000060fa005000000000060100000ea742420000000000000000`
- `levels.rpf!2!5`: 31,840 bytes, head `0000000000000000a07b005000000000060100004a0a80420000000000000000`
- `levels.rpf!2!10`: 147,824 bytes, head `0000000000000000304102500000000006010000105e44420000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!0`: 41,648 bytes, head `000000000000000010a200500000000006010000924599420000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!8`: 63,424 bytes, head `000000000000000080f70050000000000601000036812b420000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!3!13`: 151,776 bytes, head `000000000000000070ff01500000000006010000fe3346420000000000000000`
- `pack/story000/story000.rpf!6!2`: 73,920 bytes, head `0000000000000000a020015000000000060100001513a1420000000000000000`
- `pack/story000/story000.rpf!6!3`: 584,928 bytes, head `0000000000000000b0ec085000000000060100002fb5e0420000000000000000`
- `pack/story000/story000.rpf!6!6`: 73,200 bytes, head `000000000000000020fe00500000000006010000ceac68420000000000000000`

Samples of type 6 as `resource:s5:small+zero`:
- `levels.rpf!1719!0`: 77,280 bytes, head `0000000000000000a0f4005000000000060100003e0280410000000000000000`
- `levels.rpf!1719!1`: 38,048 bytes, head `00000000000000004094005000000000060100005cda89410000000000000000`
- `levels.rpf!1719!2`: 405,888 bytes, head `0000000000000000f0f905500000000006010000b6e1dd410000000000000000`

### Type 11: 48612 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 11 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zmt | 28295 | 202 |
| 11 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zmt | 18294 | 282 |
| 11 | format:rbf0 | format:rbf0 | chunked-3 | no | decoded | verified | structural | zmt | 1278 | 10 |
| 11 | format:psin | format:psin | chunked-3 | yes | decoded | verified | structural | zmt | 437 | 10 |
| 11 | format:rbf0 | format:rbf0 | raw-deflate | no | decoded | verified | structural | zmt | 156 | 1 |
| 11 | format:rbf0 | format:rbf0 | chunked-3 | yes | decoded | verified | structural | zmt | 59 | 5 |
| 11 | format:psin | format:psin | chunked-4 | no | decoded | verified | structural | zmt | 55 | 1 |
| 11 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | zmt | 33 | 1 |
| 11 | format:psin | format:psin | raw-deflate | yes | decoded | verified | structural | zmt | 4 | 4 |
| 11 | format:psin | format:psin | raw-deflate | no | decoded | verified | structural | zmt | 1 | 1 |

Samples of type 11 as `resource:s5:ptr:seg5+zero`:
- `data.rpf!8!0`: 4,688 bytes, head `0000000000000000a010005000000000304452507a0000000000000000000000`
- `data.rpf!8!1`: 7,792 bytes, head `0000000000000000c01c005000000000304452507a0000000000000000000000`
- `data.rpf!8!2`: 6,752 bytes, head `0000000000000000b018005000000000304452507a0000000000000000000000`
- `levels.rpf!12!2010`: 2,768 bytes, head `00000000000000002008005000000000304452507a0000000000000000000000`
- `levels.rpf!12!2011`: 2,288 bytes, head `00000000000000004006005000000000304452507a0000000000000000000000`
- `levels.rpf!12!2013`: 2,256 bytes, head `00000000000000002006005000000000304452507a0000000000000000000000`
- `navmeshes.rpf!26!0`: 25,488 bytes, head `0000000000000000e05a005000000000304452507a0000000000000000000000`
- `navmeshes.rpf!26!1`: 30,352 bytes, head `0000000000000000406d005000000000304452507a0000000000000000000000`
- `navmeshes.rpf!26!2`: 10,768 bytes, head `00000000000000006021005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!44!0`: 4,896 bytes, head `00000000000000005001005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!43!0`: 46,800 bytes, head `0000000000000000e0b3005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!43!1`: 196,608 bytes, head `00000000000000000065025000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!43!2`: 22,224 bytes, head `00000000000000008053005000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!13!0`: 393,216 bytes, head `000000000000000050ce035000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!13!1`: 524,288 bytes, head `0000000000000000202a065000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!13!2`: 524,288 bytes, head `0000000000000000e055065000000000304452507a0000000000000000000000`
- `packs.rpf!6!0`: 2,624 bytes, head `00000000000000006003005000000000304452507a0000000000000000000000`
- `packs.rpf!6!1`: 18,448 bytes, head `00000000000000002042005000000000304452507a0000000000000000000000`
- `packs.rpf!6!2`: 135,376 bytes, head `00000000000000007003015000000000304452507a0000000000000000000000`

Samples of type 11 as `format:psin`:
- `anim.rpf!111!0`: 2,808 bytes, head `5053494e00000800dfa8cc2810000000aaaaaaaaaaaaaaaa0101000020060000`
- `anim.rpf!196!0`: 10,008 bytes, head `5053494e000023d021000000fc130000aaaaaaaaaaaaaaaa55e401dfa0000000`
- `anim.rpf!196!1`: 11,512 bytes, head `5053494e000029b021000000dc120000aaaaaaaaaaaaaaaa55e401dfa0000000`
- `data.rpf!2!321`: 7,176 bytes, head `5053494e000007f0808637b730000000aaaaaaaaaaaaaaaa4a00000090070000`
- `data.rpf!4!321`: 7,176 bytes, head `5053494e000007f0808637b730000000aaaaaaaaaaaaaaaa4a00000090070000`
- `data.rpf!5!321`: 7,176 bytes, head `5053494e000007f0808637b730000000aaaaaaaaaaaaaaaa4a00000090070000`
- `levels.rpf!12!2012`: 320,872 bytes, head `5053494e0003aa50a210b506b8030000aaaaaaaaaaaaaaaa01000000780a0000`
- `levels.rpf!21!3493`: 581,576 bytes, head `5053494e0006bc60a210b50648030000aaaaaaaaaaaaaaaa010000001c120000`
- `levels.rpf!25!5435`: 2,504 bytes, head `5053494e00000490c90155b5c0010000aaaaaaaaaaaaaaaa2f2d2bd520000000`
- `navmeshes.rpf!0!2448`: 109,976 bytes, head `5053494e000100400001000000000100aaaaaaaaaaaaaaaa387e62cd10000000`
- `navmeshes.rpf!2!2448`: 109,976 bytes, head `5053494e000100400001000000000100aaaaaaaaaaaaaaaa387e62cd10000000`
- `navmeshes.rpf!3!2448`: 109,976 bytes, head `5053494e000100400001000000000100aaaaaaaaaaaaaaaa387e62cd10000000`
- `pack/core_restofworld/core_restofworld.rpf!20`: 34,464 bytes, head `5053494e00007550d0a9e30300360000aaaaaaaaaaaaaaaa7f9743cc60030000`
- `pack/core_restofworld/core_restofworld.rpf!25`: 67,200 bytes, head `5053494e0000b0d00101000000820000aaaaaaaaaaaaaaaa02010000081c0000`
- `pack/core_restofworld/core_restofworld.rpf!27`: 23,168 bytes, head `5053494e0000456001010000a03c0000aaaaaaaaaaaaaaaa0201000070020000`
- `pack/shared_minigame000/shared_minigame000.rpf!0!3`: 488 bytes, head `5053494e00000070a1f0d59308000000aaaaaaaaaaaaaaaa808637b730000000`
- `pack/shared_minigame000/shared_minigame000.rpf!1!3`: 488 bytes, head `5053494e00000070a1f0d59308000000aaaaaaaaaaaaaaaa808637b730000000`
- `pack/shared_minigame000/shared_minigame000.rpf!6!3`: 488 bytes, head `5053494e00000070a1f0d59308000000aaaaaaaaaaaaaaaa808637b730000000`
- `pack/story000/story000.rpf!5!319`: 2,472 bytes, head `5053494e00000220a1f0d59380000000aaaaaaaaaaaaaaaa808637b730000000`
- `pack/story000/story000.rpf!8!319`: 2,472 bytes, head `5053494e00000220a1f0d59380000000aaaaaaaaaaaaaaaa808637b730000000`
- `pack/story000/story000.rpf!42!0`: 2,656 bytes, head `5053494e000008e04c4efe40c0080000aaaaaaaaaaaaaaaa7070707070707070`
- `pack/story000/story000_script.rpf!0!0`: 13,696 bytes, head `5053494e000024600801000060000000aaaaaaaaaaaaaaaa4d00000070000000`
- `pack/story000/story000_script.rpf!0!1`: 50,376 bytes, head `5053494e00008f20bde686df18000000aaaaaaaaaaaaaaaa09010000a0000000`
- `pack/story000/story000_script.rpf!0!2`: 18,248 bytes, head `5053494e00002d600501000048030000aaaaaaaaaaaaaaaa0601000060000000`

Samples of type 11 as `format:rbf0`:
- `anim.rpf!261`: 1,348,436 bytes, head `52424630fbff010000001500726167655f5f63725269675365744d616e616765`
- `data.rpf!16!0`: 33,916 bytes, head `52424630fbff010000001d00756953657474696e677347616d65706164436f6e`
- `data.rpf!21!0`: 19,633 bytes, head `52424630fbff010000001300726167655f5f66777569466c6f77426c6f636b00`
- `data.rpf!21!1`: 2,674 bytes, head `52424630fbff0100000011007569466565646261636b436f6e74657874000000`
- `levels.rpf!1808!2`: 20,024 bytes, head `52424630fbff010000001000435065645363686564756c655061636b00000000`
- `levels.rpf!1808!11`: 8,905 bytes, head `52424630fbff010000001000435065645363686564756c655061636b00000000`
- `levels.rpf!1808!64`: 26,230 bytes, head `52424630fbff010000001000435065645363686564756c655061636b00000000`
- `pack/core_restofworld/core_restofworld.rpf!9!0`: 14,109 bytes, head `52424630fbff010000001700434d6f7669655375627469746c65436f6e746169`
- `pack/core_restofworld/core_restofworld.rpf!9!1`: 4,117 bytes, head `52424630fbff010000001700434d6f7669655375627469746c65436f6e746169`
- `pack/core_restofworld/core_restofworld.rpf!22`: 5,138 bytes, head `52424630fbff010000001e005666785465787475726541746c61734d65746164`
- `pack/story000/story000.rpf!645`: 18,906 bytes, head `52424630fbff010000001e005666785465787475726541746c61734d65746164`
- `packs.rpf!121`: 215 bytes, head `52424630fbff010000002300726167655f5f6372736d48616972426f756e644d`

Samples of type 11 as `format:psin`:
- `anim.rpf!236`: 10,064 bytes, head `5053494e00001b00744f681d40000000aaaaaaaaaaaaaaaa1c994bc5c8010000`
- `anim.rpf!240`: 14,592 bytes, head `5053494e0000281028b96e6818000000aaaaaaaaaaaaaaaa918dfb5768020000`
- `anim.rpf!243`: 1,552 bytes, head `5053494e000002604b1f649aa8000000aaaaaaaaaaaaaaaae6353d8f50010000`
- `data.rpf!23!0`: 187,816 bytes, head `5053494e0002b8f00101000040080000aaaaaaaaaaaaaaaae25989ba04330100`
- `data.rpf!23!1`: 37,192 bytes, head `5053494e000080400101000020040000aaaaaaaaaaaaaaaae25989bad8330000`
- `data.rpf!23!2`: 1,950,552 bytes, head `5053494e001d15400101000000840000aaaaaaaaaaaaaaaae25989ba94d10c00`
- `levels.rpf!2054`: 1,432 bytes, head `5053494e000001600001000060000000aaaaaaaaaaaaaaaa0101000020000000`
- `pack/core_licenses/core_licenses_data.rpf!0!0`: 1,320 bytes, head `5053494e0000028040e3659e30000000aaaaaaaaaaaaaaaa0101000020020000`
- `pack/core_licenses/core_licenses_data.rpf!0!1`: 4,152 bytes, head `5053494e000002a040e3659e30000000aaaaaaaaaaaaaaaa0101000040020000`
- `pack/story000/story000.rpf!67!0`: 2,295,324 bytes, head `5053494e001e51906bd3a23600020000aaaaaaaaaaaaaaaae6164dd710000000`
- `pack/story000/story000.rpf!67!1`: 4,784 bytes, head `5053494e00000aa09369d35e10020000aaaaaaaaaaaaaaaa0101000040060000`
- `pack/story000/story000.rpf!147!0`: 694,312 bytes, head `5053494e000927c00901000080100000aaaaaaaaaaaaaaaa0101000000c80100`
- `pack/story000/story000_script.rpf!3!0`: 2,608 bytes, head `5053494e00000340d823b6ae48000000aaaaaaaaaaaaaaaa31c6b48530020000`
- `pack/story000/story000_script.rpf!3!1`: 4,016 bytes, head `5053494e000008401600000010010000aaaaaaaaaaaaaaaa31c6b48540040000`
- `pack/story000/story000_script.rpf!3!2`: 34,240 bytes, head `5053494e000068c01600000028030000aaaaaaaaaaaaaaaa4400000070070000`
- `packs.rpf!156`: 1,432,048 bytes, head `5053494e00055a604368c0d5e8200000aaaaaaaaaaaaaaaa0101000000190000`

Samples of type 11 as `format:rbf0`:
- `data.rpf!0!0`: 12,324 bytes, head `52424630fbff0100000011007569437265646974735061676544617461000000`
- `data.rpf!0!1`: 285 bytes, head `52424630fbff0100000011007569437265646974735061676544617461000000`
- `data.rpf!0!2`: 3,883 bytes, head `52424630fbff0100000011007569437265646974735061676544617461000000`

Samples of type 11 as `format:rbf0`:
- `data.rpf!21!33`: 44,048 bytes, head `52424630fbff010000000800554953637265656e00000000000001000c004c61`
- `data.rpf!21!42`: 550 bytes, head `52424630fbff010000001000726167655f5f6677756950726566616200000000`
- `data.rpf!21!71`: 3,945 bytes, head `52424630fbff010000001000726167655f5f6677756950726566616200000000`
- `pack/story000/story000.rpf!245!14`: 190,589 bytes, head `52424630fbff010000002000416d6269656e7452756c65735f5f436f6e646974`
- `pack/story000/story000.rpf!245!52`: 85,019 bytes, head `52424630fbff010000002000416d6269656e7452756c65735f5f436f6e646974`
- `pack/story000/story000.rpf!245!56`: 12,022 bytes, head `52424630fbff010000002000416d6269656e7452756c65735f5f436f6e646974`
- `packs.rpf!60`: 122,615 bytes, head `52424630fbff010000002100726167655f5f6372736d48616972537472616e64`
- `packs.rpf!63`: 69,094 bytes, head `52424630fbff010000002a00726167655f5f6372736d48616972537472616e64`
- `packs.rpf!65`: 5,266 bytes, head `52424630fbff010000002700726167655f5f6372736d486169724d6174657269`
- `textures.rpf!21`: 899,598 bytes, head `52424630fbff010000001e005666785465787475726541746c61734d65746164`

Samples of type 11 as `format:psin`:
- `levels.rpf!1029!4065`: 2,504 bytes, head `5053494e0000068020d8566318000000aaaaaaaaaaaaaaaa013aab71a0000000`
- `levels.rpf!1029!4066`: 1,992 bytes, head `5053494e00000290c90155b5e0000000aaaaaaaaaaaaaaaa2f2d2bd520000000`
- `levels.rpf!1029!4068`: 3,592 bytes, head `5053494e000008a0c90155b580030000aaaaaaaaaaaaaaaa2f2d2bd520000000`

Samples of type 11 as `resource:s5:ptr:seg5+zero`:
- `levels.rpf!1029!4071`: 5,136 bytes, head `00000000000000006011005000000000304452507a0000000000000000000000`
- `levels.rpf!1029!4074`: 11,104 bytes, head `0000000000000000b028005000000000304452507a0000000000000000000000`
- `levels.rpf!1029!4085`: 5,296 bytes, head `00000000000000000012005000000000304452507a0000000000000000000000`

Samples of type 11 as `format:psin`:
- `pack/story000/story000.rpf!90!0`: 1,073,528 bytes, head `5053494e000a16e08b3eafcb40000000aaaaaaaaaaaaaaaaf654382a804a0500`
- `pack/story000/story000.rpf!407!0`: 13,315,952 bytes, head `5053494e0085ff500501000060000000aaaaaaaaaaaaaaaa64cc75a8680d0000`
- `pack/story000/story000.rpf!410!0`: 3,731,576 bytes, head `5053494e002572e081d7b11030810000aaaaaaaaaaaaaaaa84887a04c0010000`

Samples of type 11 as `format:psin`:
- `levels.rpf!1645!0`: 2,646,032 bytes, head `5053494e002803600001000000050000aaaaaaaaaaaaaaaa2523056600a60e00`

### Type 14: 2 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 14 | none | binary:30030100 | chunked-3 | no | decoded | unknown | bytes | zdatb | 1 | 1 |
| 14 | none | binary:58340400 | chunked-3 | yes | decoded | unknown | bytes | zdatb | 1 | 1 |

Samples of type 14 as `binary:30030100`:
- `data.rpf!262`: 1,280 bytes, head `30030100000500000100100043003003200300100100100008000000b0030000`

Samples of type 14 as `binary:58340400`:
- `pack/story000/story000_script.rpf!2!0`: 672,576 bytes, head `5834040040430a001d001c0000000000583402006811000000000000a409011c`

### Type 15: 250434 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 15 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zbdr | 245666 | 1203 |
| 15 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-4 | no | decoded | unknown | resource | zbdr | 4768 | 1 |

Samples of type 15 as `resource:s5:small+ptr:seg5`:
- `pack/core_bvh4/core_bvh4.rpf!0!0`: 5,840 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!0!1`: 1,376,464 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!0!2`: 9,424 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!1`: 4,816 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!2`: 131,280 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!3`: 976 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`

Samples of type 15 as `resource:s5:small+ptr:seg5`:
- `pack/core_bvh4/core_bvh4.rpf!772!0`: 131,280 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!772!1`: 196,816 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!772!2`: 11,216 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`

### Type 16: 22382 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 16 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zbdd | 22126 | 131 |
| 16 | resource:segment-5 | resource:s5:zero+small | chunked-4 | no | decoded | unknown | resource | zbdd | 256 | 1 |

Samples of type 16 as `resource:s5:zero+small`:
- `pack/core_bvh4/core_bvh4.rpf!2!1`: 272 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/core_bvh4/core_bvh4.rpf!2!8`: 272 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/core_bvh4/core_bvh4.rpf!2!13`: 272 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!0`: 272 bytes, head `0000000000000000e00000500000000000000000000000000100000000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!8`: 192 bytes, head `0000000000000000800000500000000000000000000000000100000000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!0!20`: 160 bytes, head `0000000000000000600000500000000000000000000000000100000000000000`

Samples of type 16 as `resource:s5:zero+small`:
- `pack/core_bvh4/core_bvh4.rpf!772!8`: 368 bytes, head `0000000000000000300100500000000000000000000000000100000000000000`
- `pack/core_bvh4/core_bvh4.rpf!772!13`: 240 bytes, head `0000000000000000a00000500000000000000000000000000100000000000000`
- `pack/core_bvh4/core_bvh4.rpf!772!31`: 160 bytes, head `0000000000000000600000500000000000000000000000000100000000000000`

### Type 17: 22440 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 17 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zbft | 22440 | 263 |

Samples of type 17 as `resource:s5:small+ptr:seg5`:
- `pack/core_bvh4/core_bvh4.rpf!11!0`: 1,114,368 bytes, head `0000000000000000b0000050000000000200000000000000d000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!11!1`: 1,310,928 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/core_bvh4/core_bvh4.rpf!11!2`: 5,072 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!2!8`: 3,280 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!2!29`: 131,280 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!2!41`: 131,280 bytes, head `000000000000000080000050000000000100000000000000a000005000000000`

### Type 18: 611 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 18 | resource:segment-5 | resource:s5:other+other | chunked-2 | no | decoded | unknown | resource | zvert | 611 | 4 |

Samples of type 18 as `resource:s5:other+other`:
- `levels.rpf!1644!89`: 127,696 bytes, head `0000000000000000000800500000000028080050000000000500050000000000`
- `levels.rpf!1644!179`: 101,744 bytes, head `0000000000000000000800500000000028080050000000000500050000000000`
- `levels.rpf!1644!324`: 78,608 bytes, head `0000000000000000000800500000000028080050000000000500050000000000`
- `levels.rpf!1644!0`: 89,296 bytes, head `0000000000000000f01400500000000070100050000000000d000d0000000000`
- `levels.rpf!1644!1`: 132,480 bytes, head `0000000000000000400500500000000060050050000000000300030000000000`
- `levels.rpf!1644!2`: 145,472 bytes, head `0000000000000000900e005000000000400e0050000000000900090000000000`

### Type 64: 443 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 64 | signature:Observed("move") | signature:Observed("move") | chunked-3 | no | decoded | unknown | bytes | mrf | 443 | 2 |

Samples of type 64 as `signature:Observed("move")`:
- `anim.rpf!43!0`: 12,738 bytes, head `4d6f5645130000000000000000000000000000004a8509009431000000000000`
- `anim.rpf!43!1`: 4,454 bytes, head `4d6f56451300000000000000000000000000000064e4bd003811000000000000`
- `anim.rpf!43!2`: 754 bytes, head `4d6f564513000000000000000000000000000000513edb00c402000000000000`
- `pack/story000/story000.rpf!84!0`: 871 bytes, head `4d6f56451300000000000000000000000000000063782e003403000000000000`
- `pack/story000/story000.rpf!84!1`: 754 bytes, head `4d6f56451300000000000000000000000000000084ec5500c402000000000000`
- `pack/story000/story000.rpf!84!2`: 3,935 bytes, head `4d6f5645130000000000000000000000000000003de85c002c0f000000000000`

### Type 66: 87 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 66 | format:gfx | format:gfx | chunked-3 | no | decoded | verified | structural | gfx | 87 | 7 |

Samples of type 66 as `format:gfx`:
- `data.rpf!1!3`: 21,133 bytes, head `4746582a8d52000070000b540000b540001e01001bfa0104000000000e00000f`
- `data.rpf!1!4`: 12,107 bytes, head `4746582a4b2f00008000026d4000018600001e010013fa0104000000000e0000`
- `data.rpf!1!5`: 1,379,793 bytes, head `4746582ad10d15008800012c0000002a3000001e010011fa0104000000000e00`

### Type 67: 62384 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 67 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zcd | 62375 | 383 |
| 67 | resource:segment-5 | resource:s5:zero+zero | chunked-4 | no | decoded | unknown | resource | zcd | 9 | 1 |

Samples of type 67 as `resource:s5:zero+zero`:
- `anim.rpf!5!0`: 73,424 bytes, head `0000000000000000f01d01500000000000000000000000000000000000000000`
- `anim.rpf!5!1`: 421,776 bytes, head `0000000000000000e06d06500000000000000000000000000000000000000000`
- `anim.rpf!5!2`: 13,696 bytes, head `0000000000000000903400500000000000000000000000000000000000000000`
- `levels.rpf!21!3480`: 17,280 bytes, head `0000000000000000104300500000000000000000000000000000000000000000`
- `levels.rpf!21!3483`: 10,336 bytes, head `0000000000000000e02700500000000000000000000000000000000000000000`
- `levels.rpf!59!297`: 3,568 bytes, head `0000000000000000a00d00500000000000000000000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!8!128`: 1,504 bytes, head `0000000000000000900500500000000000000000000000000000000000000000`
- `pack/core_restofworld001/core_restofworld001.rpf!0!0`: 131,072 bytes, head `000000000000000020b201500000000000000000000000000000000000000000`
- `pack/core_restofworld001/core_restofworld001.rpf!0!1`: 68,752 bytes, head `0000000000000000f00b01500000000000000000000000000000000000000000`
- `pack/core_restofworld001/core_restofworld001.rpf!0!2`: 65,536 bytes, head `000000000000000000bc00500000000000000000000000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!33!143`: 37,488 bytes, head `0000000000000000f08f00500000000000000000000000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!46!473`: 4,912 bytes, head `0000000000000000801200500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!4!11`: 555,296 bytes, head `0000000000000000207708500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!4!29`: 62,048 bytes, head `0000000000000000c0f000500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!4!47`: 32,272 bytes, head `0000000000000000407d00500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!1!0`: 323,376 bytes, head `0000000000000000103503500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!1!1`: 2,728,384 bytes, head `0000000000000000c09a29500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!1!2`: 55,424 bytes, head `0000000000000000e0d700500000000000000000000000000000000000000000`

Samples of type 67 as `resource:s5:zero+zero`:
- `levels.rpf!1719!4983`: 2,480 bytes, head `0000000000000000500900500000000000000000000000000000000000000000`
- `levels.rpf!1719!4984`: 2,336 bytes, head `0000000000000000c00800500000000000000000000000000000000000000000`
- `levels.rpf!1719!4985`: 1,488 bytes, head `0000000000000000800500500000000000000000000000000000000000000000`

### Type 69: 1 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 69 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zpmd | 1 | 1 |

Samples of type 69 as `resource:s5:zero+zero`:
- `anim.rpf!95!0`: 20,704 bytes, head `0000000000000000404f00500000000000000000000000000000000000000000`

### Type 70: 8443 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 70 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zpm | 8443 | 67 |

Samples of type 70 as `resource:s5:zero+zero`:
- `anim.rpf!0!0`: 16,368 bytes, head `0000000000000000d03800500000000000000000000000000000000000000000`
- `anim.rpf!2!0`: 6,576 bytes, head `0000000000000000701800500000000000000000000000000000000000000000`
- `anim.rpf!2!1`: 12,064 bytes, head `0000000000000000b02c00500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!341!0`: 65,360 bytes, head `0000000000000000c0f400500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!427!0`: 6,496 bytes, head `0000000000000000701700500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!427!1`: 9,968 bytes, head `0000000000000000702300500000000000000000000000000000000000000000`

### Type 72: 226 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 72 | resource:segment-5 | resource:s5:other+zero | chunked-2 | no | decoded | unknown | resource | zpt | 226 | 13 |

Samples of type 72 as `resource:s5:other+zero`:
- `data.rpf!29!0`: 92,336 bytes, head `000000000000000040f600500000000008fc0050000000000000000000000000`
- `data.rpf!29!2`: 201,808 bytes, head `000000000000000000ec015000000000883d0250000000000000000000000000`
- `data.rpf!29!3`: 477,824 bytes, head `0000000000000000e0f7045000000000e8d40550000000000000000000000000`
- `data.rpf!29!6`: 54,528 bytes, head `0000000000000000009a005000000000209c0050000000000000000000000000`
- `data.rpf!29!8`: 20,112 bytes, head `0000000000000000804400500000000080450050000000000000000000000000`
- `data.rpf!29!9`: 485,904 bytes, head `0000000000000000800805500000000010000650000000000000000000000000`
- `data.rpf!29!132`: 28,576 bytes, head `0000000000000000406500500000000028660050000000000000000000000000`
- `data.rpf!29!103`: 18,048 bytes, head `0000000000000000003c005000000000443d0050000000000000000000000000`
- `data.rpf!29!42`: 34,304 bytes, head `0000000000000000607100500000000058730050000000000000000000000000`
- `data.rpf!29!121`: 36,192 bytes, head `0000000000000000606c005000000000686d0050000000000000000000000000`
- `data.rpf!29!1`: 18,672 bytes, head `0000000000000000c03e005000000000783f0050000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!5!0`: 695,696 bytes, head `000000000000000030890750000000002a4d0950000000000000000000000000`
- `pack/story000/story000.rpf!295!3`: 127,184 bytes, head `0000000000000000704d015000000000fc7f0150000000000000000000000000`
- `pack/story000/story000.rpf!295!8`: 262,880 bytes, head `0000000000000000e010035000000000886d0350000000000000000000000000`
- `pack/story000/story000.rpf!295!11`: 281,600 bytes, head `0000000000000000f091025000000000f4120350000000000000000000000000`
- `pack/story000/story000.rpf!295!0`: 91,152 bytes, head `0000000000000000b0fc00500000000040170150000000000000000000000000`
- `pack/story000/story000.rpf!295!1`: 84,592 bytes, head `000000000000000000ef005000000000800d0150000000000000000000000000`
- `pack/story000/story000.rpf!295!2`: 19,360 bytes, head `0000000000000000b04100500000000000420050000000000000000000000000`
- `pack/story000/story000.rpf!295!47`: 10,528 bytes, head `0000000000000000002400500000000038240050000000000000000000000000`
- `pack/story000/story000.rpf!295!56`: 28,528 bytes, head `0000000000000000e05f00500000000048610050000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!12!0`: 417,328 bytes, head `0000000000000000807704500000000060400550000000000000000000000000`

### Type 73: 166072 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 73 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zmap | 161985 | 312 |
| 73 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | zmap | 4087 | 4 |

Samples of type 73 as `resource:s5:ptr:seg5+zero`:
- `levels.rpf!19!0`: 4,960 bytes, head `00000000000000008005005000000000304452507a0000000000000000000000`
- `levels.rpf!19!1`: 49,824 bytes, head `00000000000000006076005000000000304452507a0000000000000000000000`
- `levels.rpf!19!2`: 49,936 bytes, head `000000000000000060b7005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!0`: 3,888 bytes, head `0000000000000000c004005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!1`: 7,968 bytes, head `0000000000000000700e005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!2`: 17,472 bytes, head `0000000000000000802a005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!0`: 8,096 bytes, head `0000000000000000900e005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!1`: 17,488 bytes, head `0000000000000000102b005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!2`: 17,632 bytes, head `0000000000000000102b005000000000304452507a0000000000000000000000`

Samples of type 73 as `resource:s5:ptr:seg5+zero`:
- `levels.rpf!772!0`: 1,263,616 bytes, head `0000000000000000403c135000000000304452507a0000000000000000000000`
- `levels.rpf!927!0`: 6,384 bytes, head `0000000000000000e006005000000000304452507a0000000000000000000000`
- `levels.rpf!927!1`: 144,448 bytes, head `0000000000000000900a005000000000304452507a0000000000000000000000`

### Type 74: 6308 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 74 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | ztyp | 6135 | 589 |
| 74 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-4 | no | decoded | unknown | resource | ztyp | 173 | 2 |

Samples of type 74 as `resource:s5:ptr:seg5+zero`:
- `levels.rpf!0!0`: 189,440 bytes, head `00000000000000005085025000000000304452507a0000000000000000000000`
- `levels.rpf!0!1`: 177,456 bytes, head `00000000000000007064025000000000304452507a0000000000000000000000`
- `levels.rpf!0!2`: 131,072 bytes, head `0000000000000000207e015000000000304452507a0000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!0!0`: 69,488 bytes, head `0000000000000000e0a7005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!4`: 22,704 bytes, head `0000000000000000c044005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!5`: 1,840 bytes, head `00000000000000000002005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!2!6`: 21,712 bytes, head `0000000000000000303c005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!68`: 23,728 bytes, head `0000000000000000f046005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!69`: 6,640 bytes, head `0000000000000000b010005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!10!70`: 21,344 bytes, head `0000000000000000e03c005000000000304452507a0000000000000000000000`
- `packs.rpf!18!45`: 17,008 bytes, head `0000000000000000b022005000000000304452507a0000000000000000000000`
- `packs.rpf!46!2490`: 917,504 bytes, head `0000000000000000e032075000000000304452507a0000000000000000000000`

Samples of type 74 as `resource:s5:ptr:seg5+zero`:
- `levels.rpf!1029!4063`: 4,000 bytes, head `00000000000000006008005000000000304452507a0000000000000000000000`
- `levels.rpf!1029!4064`: 8,576 bytes, head `0000000000000000e012005000000000304452507a0000000000000000000000`
- `levels.rpf!1029!4067`: 121,120 bytes, head `00000000000000000093015000000000304452507a0000000000000000000000`

### Type 77: 3 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 77 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zjd | 3 | 1 |

Samples of type 77 as `resource:s5:zero+small`:
- `anim.rpf!200!0`: 5,104 bytes, head `0000000000000000b01300500000000000000000000000000100000000000000`
- `anim.rpf!200!1`: 19,168 bytes, head `0000000000000000c04a00500000000000000000000000000100000000000000`
- `anim.rpf!200!2`: 3,968 bytes, head `0000000000000000500f00500000000000000000000000000100000000000000`

### Type 78: 25608 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 78 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zad | 25608 | 131 |

Samples of type 78 as `resource:s5:zero+zero`:
- `pack/story000/story000.rpf!4!0`: 33,488 bytes, head `0000000000000000b08200500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!4!1`: 131,072 bytes, head `0000000000000000207201500000000000000000000000000000000000000000`
- `pack/story000/story000.rpf!4!2`: 1,152 bytes, head `0000000000000000600400500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!2!0`: 196,608 bytes, head `0000000000000000c0db02500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!2!1`: 992 bytes, head `0000000000000000c00300500000000000000000000000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!2!2`: 10,160 bytes, head `0000000000000000902700500000000000000000000000000000000000000000`

### Type 79: 27644 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 79 | resource:segment-5 | resource:s5:small+zero | chunked-2 | no | decoded | unknown | resource | znv | 27644 | 12 |

Samples of type 79 as `resource:s5:small+zero`:
- `navmeshes.rpf!0!0`: 141,040 bytes, head `0000000000000000702602500000000009000000150001000000000000000000`
- `navmeshes.rpf!0!1`: 393,216 bytes, head `000000000000000080f405500000000003000000150001000000000000000000`
- `navmeshes.rpf!0!2`: 136,784 bytes, head `0000000000000000d01502500000000009000000150001000000000000000000`

### Type 86: 11 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 86 | resource:segment-5 | resource:s5:zero+small | chunked-2 | no | decoded | unknown | resource | zfd | 11 | 1 |

Samples of type 86 as `resource:s5:zero+small`:
- `anim.rpf!99!0`: 64,080 bytes, head `000000000000000030fa00500000000000000000000000000100000000000000`
- `anim.rpf!99!1`: 46,416 bytes, head `000000000000000030b500500000000000000000000000000100000000000000`
- `anim.rpf!99!2`: 400 bytes, head `0000000000000000600100500000000000000000000000000100000000000000`

### Type 87: 15067 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 87 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zas | 15067 | 185 |

Samples of type 87 as `resource:s5:ptr:seg5+zero`:
- `anim.rpf!1!0`: 255,200 bytes, head `0000000000000000506d035000000000304452507a0000000000000000000000`
- `anim.rpf!1!1`: 203,120 bytes, head `000000000000000070be025000000000304452507a0000000000000000000000`
- `anim.rpf!1!2`: 241,920 bytes, head `0000000000000000403a035000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!1!0`: 706,144 bytes, head `0000000000000000e0ff095000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!1!1`: 197,920 bytes, head `00000000000000002058025000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!1!2`: 207,856 bytes, head `00000000000000008072025000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!5!0`: 225,568 bytes, head `0000000000000000f0a6025000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!5!1`: 73,936 bytes, head `000000000000000090c8005000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!5!2`: 79,936 bytes, head `00000000000000002096005000000000304452507a0000000000000000000000`

### Type 88: 40019 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 88 | resource:segment-5 | resource:s5:zero+other | chunked-2 | no | decoded | unknown | resource | zsm | 40019 | 10 |

Samples of type 88 as `resource:s5:zero+other`:
- `pack/core_restofworld/core_restofworld.rpf!7!0`: 2,496 bytes, head `0000000000000000e001005000000000000000000000000000000300b33d8f7d`
- `pack/core_restofworld/core_restofworld.rpf!7!1`: 2,448 bytes, head `0000000000000000f001005000000000000000000000000000000300b33d8f7d`
- `pack/core_restofworld/core_restofworld.rpf!7!2`: 3,328 bytes, head `00000000000000000002005000000000000000000000000000000300b33d8f7d`
- `pack/shared_minigame000/shared_minigame000.rpf!19!0`: 35,936 bytes, head `0000000000000000008c00500000000000000000000000000000027f00000000`
- `pack/shared_minigame000/shared_minigame000.rpf!19!1`: 1,088 bytes, head `00000000000000002004005000000000000000000000000000ff0500b33d8f7d`
- `pack/shared_minigame000/shared_minigame000.rpf!19!2`: 28,032 bytes, head `0000000000000000506d00500000000000000000000000000000027f00000000`
- `packs.rpf!2!16`: 67,200 bytes, head `0000000000000000d00501500000000050060150000000000100027f00000000`
- `packs.rpf!2!31`: 266,208 bytes, head `0000000000000000900f045000000000d00f0450000000000100027f00000000`
- `packs.rpf!2!77`: 17,856 bytes, head `00000000000000008045005000000000a0450050000000000100020000000000`
- `packs.rpf!2!0`: 800 bytes, head `00000000000000000003005000000000000000000000000000ff0500b33d8f7d`
- `packs.rpf!2!1`: 800 bytes, head `00000000000000000003005000000000000000000000000000ff0500b33d8f7d`
- `packs.rpf!2!2`: 31,104 bytes, head `0000000000000000507900500000000000000000000000000000020000000000`
- `packs.rpf!2!434`: 23,232 bytes, head `0000000000000000805a00500000000000000000000000000000025500000000`
- `packs.rpf!2!540`: 91,088 bytes, head `0000000000000000906301500000000000000000000000000000025f00000000`
- `packs.rpf!2!938`: 55,600 bytes, head `000000000000000000d900500000000000000000000000000000025000000000`
- `packs.rpf!2!53`: 55,600 bytes, head `000000000000000000d900500000000000000000000000000000026400000000`
- `packs.rpf!2!251`: 27,888 bytes, head `0000000000000000b06c00500000000000000000000000000000026900000000`
- `packs.rpf!2!283`: 31,104 bytes, head `0000000000000000507900500000000000000000000000000000026e00000000`

### Type 89: 746 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 89 | resource:segment-5 | resource:s5:other+small | chunked-2 | yes | decoded | unknown | resource | zscript | 746 | 11 |

Samples of type 89 as `resource:s5:other+small`:
- `pack/story000/story000_script.rpf!1!0`: 66,768 bytes, head `0000000000000000e0ff0050000000008f444300010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!1`: 151,648 bytes, head `00000000000000004050025000000000c14c4300010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!2`: 198,064 bytes, head `0000000000000000e0fe0250000000001d714500010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!252`: 186,880 bytes, head `000000000000000070f701500000000060268d55010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!299`: 220,992 bytes, head `000000000000000080be02500000000030e8f268010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!314`: 1,310,720 bytes, head `0000000000000000a0ab135000000000503e656c010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!163`: 155,232 bytes, head `0000000000000000a0fd01500000000021394f39010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!210`: 12,368 bytes, head `000000000000000020300050000000002d793946010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!214`: 131,072 bytes, head `0000000000000000d0490150000000004a3b3148010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!362`: 6,272 bytes, head `000000000000000040180050000000005d5f7e7c010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!267`: 26,656 bytes, head `0000000000000000f0670050000000007856525c010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!222`: 21,072 bytes, head `000000000000000020520050000000007930534b010000006f00000067cedbea`
- `pack/story000/story000_script.rpf!1!93`: 76,848 bytes, head `0000000000000000f02b0150000000007e726321010000006f00000067cedbea`
- `script.rpf!0!0`: 1,310,720 bytes, head `0000000000000000903f13500000000085af07b4010000006f00000067cedbea`

### Type 93: 211 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 93 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zfc | 211 | 1 |

Samples of type 93 as `format:psin`:
- `packs.rpf!1!0`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!1`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!5`: 776 bytes, head `5053494e000000b0176b1c0590000000aaaaaaaaaaaaaaaa7070707070707070`

### Type 94: 80 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 94 | format:psin | format:psin | chunked-3 | no | decoded | verified | structural | zlfc | 80 | 1 |

Samples of type 94 as `format:psin`:
- `packs.rpf!1!2`: 344 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!3`: 360 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`
- `packs.rpf!1!4`: 360 bytes, head `5053494e00000030607b6ed90c000000aaaaaaaaaaaaaaaa7070707070707070`

### Type 95: 518 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 95 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zcg | 518 | 2 |

Samples of type 95 as `resource:s5:small+ptr:seg5`:
- `packs.rpf!0!0`: 12,160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`
- `packs.rpf!0!2`: 12,160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`
- `packs.rpf!0!4`: 12,160 bytes, head `0000000000000000602f005000000000fc2e0000fc2e00006000005000000000`

### Type 96: 1 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 96 | none | zeros | chunked-3 | no | decoded | unknown | bytes | zasd | 1 | 1 |

Samples of type 96 as `zeros`:
- `script.rpf!0!1`: 2,702,384 bytes, head `0000000000000000000000000000000000000000db7700000000000000000000`

### Type 99: 98 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 99 | resource:segment-5 | resource:s5:other+small | chunked-2 | no | decoded | unknown | resource | zcps | 98 | 4 |

Samples of type 99 as `resource:s5:other+small`:
- `packs.rpf!56!0`: 2,208 bytes, head `00000000000000008008005000000000aad07f01aad07f014e0000004e000000`
- `packs.rpf!56!1`: 2,016 bytes, head `0000000000000000c00700500000000057930306579303064e0000004e000000`
- `packs.rpf!56!2`: 1,680 bytes, head `00000000000000007006005000000000fc8b870cfc8b870c6b0000006b000000`
- `packs.rpf!56!31`: 832 bytes, head `0000000000000000c0020050000000007076b45c7076b45c0300000003000000`
- `packs.rpf!56!32`: 1,744 bytes, head `0000000000000000b0060050000000009035e25d9035e25d7100000071000000`
- `packs.rpf!56!41`: 1,536 bytes, head `0000000000000000e0050050000000009066726c9066726c5f0000005f000000`
- `packs.rpf!56!52`: 736 bytes, head `000000000000000070020050000000003246757d3246757d0400000004000000`

### Type 100: 27482 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 100 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zsp | 27482 | 11 |

Samples of type 100 as `resource:s5:small+ptr:seg5`:
- `navmeshes.rpf!1!0`: 196,608 bytes, head `00000000000000009079025000000000000200004c1600006000005000000000`
- `navmeshes.rpf!1!1`: 196,608 bytes, head `0000000000000000c08002500000000000020000161800006000005000000000`
- `navmeshes.rpf!1!2`: 38,720 bytes, head `0000000000000000209700500000000080000000af0300006000005000000000`

### Type 101: 5 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 101 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | ztsl | 5 | 1 |

Samples of type 101 as `resource:s5:ptr:seg5+zero`:
- `packs.rpf!36!0`: 13,824 bytes, head `0000000000000000800000500000000020000050000000000000000000000000`
- `packs.rpf!36!1`: 53,648 bytes, head `0000000000000000800000500000000020000050000000000000000000000000`
- `packs.rpf!36!2`: 53,648 bytes, head `0000000000000000800000500000000020000050000000000000000000000000`

### Type 102: 142 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 102 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zmmd | 142 | 13 |

Samples of type 102 as `resource:s5:zero+zero`:
- `anim.rpf!3!0`: 29,648 bytes, head `0000000000000000707000500000000000000000000000000000000000000000`
- `anim.rpf!28!0`: 11,952 bytes, head `0000000000000000e02c00500000000000000000000000000000000000000000`
- `anim.rpf!36!0`: 24,160 bytes, head `0000000000000000e05a00500000000000000000000000000000000000000000`

### Type 103: 6762 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 103 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zfid | 6762 | 17 |

Samples of type 103 as `resource:s5:ptr:seg5+zero`:
- `pack/core_restofworld/core_restofworld.rpf!2!795`: 131,312 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!2!796`: 5,072 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`
- `pack/core_restofworld/core_restofworld.rpf!2!797`: 13,712 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`
- `packs.rpf!11!519`: 5,072 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`
- `packs.rpf!11!520`: 131,312 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`
- `packs.rpf!11!521`: 13,712 bytes, head `0000000000000000d00000500000000070000050000000000000000000000000`

### Type 104: 1476 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 104 | none | binary:01000102 | chunked-3 | no | decoded | unknown | bytes | zmsk | 1476 | 1 |

Samples of type 104 as `binary:01000102`:
- `levels.rpf!69!0`: 32 bytes, head `0100010280008000000000008000800000000000000000000000000000000000`
- `levels.rpf!69!1`: 32 bytes, head `0100010280008000000000008000800000000000000000000000000000000000`
- `levels.rpf!69!2`: 27,152 bytes, head `01000102800080000300000080008000000080009000103a00000000f8300000`

### Type 105: 1476 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 105 | none | binary:50414d48 | chunked-3 | no | decoded | unknown | bytes | zhdat | 1476 | 1 |

Samples of type 105 as `binary:50414d48`:
- `levels.rpf!1237!0`: 8,748 bytes, head `50414d480132375f313500744000400000000000000020c5000097c300000044`
- `levels.rpf!1237!1`: 8,748 bytes, head `50414d480131315f3138007440004000000000c6000080c4000097c30000f0c5`
- `levels.rpf!1237!2`: 8,748 bytes, head `50414d4801345f313500687440004000000038c6000020c5000097c3000030c6`

### Type 108: 32878 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 108 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zascd | 32878 | 4 |

Samples of type 108 as `resource:s5:ptr:seg5+zero`:
- `anim.rpf!26!0`: 1,764,112 bytes, head `0000000000000000d0fc195000000000304452507a0000000000000000000000`
- `anim.rpf!26!1`: 335,968 bytes, head `0000000000000000c0d7045000000000304452507a0000000000000000000000`
- `anim.rpf!26!2`: 379,312 bytes, head `0000000000000000e0ff045000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!142!0`: 127,600 bytes, head `0000000000000000e0ff005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!142!1`: 127,616 bytes, head `000000000000000040a2015000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!142!2`: 109,344 bytes, head `0000000000000000a0ff005000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!4!0`: 65,536 bytes, head `00000000000000005087005000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!4!1`: 65,536 bytes, head `00000000000000005087005000000000304452507a0000000000000000000000`
- `pack/story000_restofworld/story000_restofworld.rpf!4!2`: 65,536 bytes, head `0000000000000000c086005000000000304452507a0000000000000000000000`

### Type 109: 4 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 109 | resource:segment-5 | resource:s5:zero+zero | chunked-2 | no | decoded | unknown | resource | zrd | 4 | 4 |

Samples of type 109 as `resource:s5:zero+zero`:
- `anim.rpf!12!0`: 95,936 bytes, head `0000000000000000a07601500000000000000000000000000000000000000000`
- `anim.rpf!25!0`: 1,247,136 bytes, head `0000000000000000800713500000000000000000000000000000000000000000`
- `anim.rpf!163!0`: 9,709,120 bytes, head `0000000000000000202694500000000000000000000000000000000000000000`

### Type 110: 5 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 110 | resource:segment-5 | resource:s5:small+ptr:seg5 | chunked-2 | no | decoded | unknown | resource | zsmam | 5 | 5 |

Samples of type 110 as `resource:s5:small+ptr:seg5`:
- `pack/core_restofworld/core_restofworld.rpf!3!0`: 1,360 bytes, head `0000000000000000200500500000000002000000060000006000005000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!36!0`: 1,584 bytes, head `0000000000000000e005005000000000020000000b0000006000005000000000`
- `packs.rpf!4!0`: 496,896 bytes, head `0000000000000000e04f07500000000000020000a91900006000005000000000`
- `packs.rpf!5!0`: 288,976 bytes, head `0000000000000000c01204500000000000010000500b00006000005000000000`
- `packs.rpf!15!0`: 3,648 bytes, head `0000000000000000e00c00500000000004000000290000006000005000000000`

### Type 111: 30511 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 111 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zldbmt | 30511 | 39 |

Samples of type 111 as `resource:s5:ptr:seg5+zero`:
- `data.rpf!2!0`: 1,840 bytes, head `0000000000000000e005005000000000304452507a0000000000000000000000`
- `data.rpf!2!1`: 26,464 bytes, head `00000000000000001066005000000000304452507a0000000000000000000000`
- `data.rpf!2!2`: 27,264 bytes, head `00000000000000003069005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!0!0`: 28,320 bytes, head `0000000000000000506d005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!0!1`: 1,952 bytes, head `00000000000000005006005000000000304452507a0000000000000000000000`
- `pack/shared_minigame000/shared_minigame000.rpf!0!2`: 1,600 bytes, head `0000000000000000f004005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!5!0`: 3,200 bytes, head `0000000000000000300b005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!5!1`: 27,152 bytes, head `0000000000000000c068005000000000304452507a0000000000000000000000`
- `pack/story000/story000.rpf!5!2`: 3,744 bytes, head `0000000000000000500d005000000000304452507a0000000000000000000000`

### Type 113: 2715 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 113 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zkit | 2715 | 1 |

Samples of type 113 as `resource:s5:ptr:seg5+zero`:
- `packs.rpf!55!0`: 101,952 bytes, head `0000000000000000b03e015000000000304452507a0000000000000000000000`
- `packs.rpf!55!1`: 232,608 bytes, head `000000000000000000ee025000000000304452507a0000000000000000000000`
- `packs.rpf!55!2`: 64,640 bytes, head `000000000000000080c3005000000000304452507a0000000000000000000000`

### Type 114: 518 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 114 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zcgc | 518 | 3 |

Samples of type 114 as `resource:s5:ptr:seg5+zero`:
- `packs.rpf!0!1`: 1,114,288 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`
- `packs.rpf!0!3`: 4,849,840 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`
- `packs.rpf!0!5`: 1,114,288 bytes, head `0000000000000000900000500000000030000050000000000000000000000000`
- `packs.rpf!40!13`: 1,600 bytes, head `0000000000000000200600500000000000000000000000003000005000000000`
- `packs.rpf!40!21`: 1,744 bytes, head `0000000000000000b00600500000000000000000000000003000005000000000`
- `packs.rpf!40!22`: 131,072 bytes, head `0000000000000000b02901500000000000000000000000003000005000000000`

### Type 115: 8415 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 115 | resource:segment-5 | resource:s5:ptr:seg5+zero | chunked-2 | no | decoded | unknown | resource | zcov | 8415 | 4 |

Samples of type 115 as `resource:s5:ptr:seg5+zero`:
- `navmeshes.rpf!9!0`: 9,120 bytes, head `00000000000000002019005000000000304452507a0000000000000000000000`
- `navmeshes.rpf!9!1`: 37,456 bytes, head `00000000000000009087005000000000304452507a0000000000000000000000`
- `navmeshes.rpf!9!2`: 262,144 bytes, head `000000000000000060ab035000000000304452507a0000000000000000000000`

### Type 255: 73068 entries

| Type | Identification | Variant | Storage | Transform | Payload | Structure | Capability | Extension | Entries | Archives |
| ---- | -------------- | ------- | ------- | --------- | ------- | --------- | ---------- | --------- | ------: | -------: |
| 255 | format:adat | format:adat | stored | no | decoded | verified | structural | - | 71676 | 122 |
| 255 | format:kb2 | format:kb2 | stored | no | decoded | verified | structural | - | 797 | 4 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | no | decoded | verified | text | xml | 96 | 10 |
| 255 | none | binary:12000000 | chunked-3 | no | decoded | unknown | bytes | - | 82 | 67 |
| 255 | xml:timecycle_modifier_data | xml:timecycle_modifier_data | chunked-3 | no | decoded | verified | text | xml | 49 | 1 |
| 255 | xml:rage__bgCrackType | xml:rage__bgCrackType | chunked-3 | yes | decoded | verified | text | xml | 36 | 1 |
| 255 | xml:CVehiclePoints | xml:CVehiclePoints | chunked-3 | no | decoded | verified | text | xml | 32 | 1 |
| 255 | xml:timecycle_keyframe_data | xml:timecycle_keyframe_data | chunked-3 | no | decoded | verified | text | xml | 27 | 1 |
| 255 | xml:CTuningFile | xml:CTuningFile | chunked-3 | yes | decoded | verified | text | xml | 24 | 1 |
| 255 | xml:CDataFileMgr__ContentChangeSetDef | xml:CDataFileMgr__ContentChangeSetDef | chunked-3 | yes | decoded | verified | text | xml | 21 | 1 |
| 255 | xml:CDataFileMgr__ContentDef | xml:CDataFileMgr__ContentDef | chunked-3 | no | decoded | verified | text | xml | 11 | 10 |
| 255 | xml:CTuningFile | xml:CTuningFile | chunked-3 | no | decoded | verified | text | xml | 10 | 1 |
| 255 | xml:SSetupData | xml:SSetupData | chunked-3 | no | decoded | verified | text | xml | 10 | 10 |
| 255 | none | text | chunked-3 | yes | decoded | unknown | bytes | - | 9 | 1 |
| 255 | xml:WaveData | xml:WaveData | chunked-3 | yes | decoded | verified | text | xml | 6 | 1 |
| 255 | format:edup | format:edup | chunked-3 | no | decoded | verified | structural | - | 5 | 5 |
| 255 | xml:CDamageDataManager | xml:CDamageDataManager | chunked-3 | no | decoded | verified | text | xml | 5 | 1 |
| 255 | xml:GridAtlasInfo | xml:GridAtlasInfo | chunked-3 | no | decoded | verified | text | xml | 4 | 1 |
| 255 | xml:CCoverProcessorTuning | xml:CCoverProcessorTuning | chunked-3 | no | decoded | verified | text | xml | 3 | 1 |
| 255 | format:psin | format:psin | chunked-3 | yes | decoded | verified | structural | - | 2 | 1 |
| 255 | signature:Observed("mhiu") | signature:Observed("mhiu") | chunked-3 | no | decoded | unknown | bytes | - | 2 | 1 |
| 255 | signature:Observed("sgd5") | signature:Observed("sgd5") | stored | no | decoded | unknown | bytes | - | 2 | 1 |
| 255 | xml:CVehiclePerformanceMaps | xml:CVehiclePerformanceMaps | chunked-3 | no | decoded | verified | text | xml | 2 | 1 |
| 255 | xml:ShoreWavePlacementData | xml:ShoreWavePlacementData | chunked-3 | no | decoded | verified | text | xml | 2 | 2 |
| 255 | xml:VehicleControlsInfo | xml:VehicleControlsInfo | chunked-3 | yes | decoded | verified | text | xml | 2 | 1 |
| 255 | xml:unvalidated | xml:unvalidated | chunked-3 | no | decoded | tentative | text | - | 2 | 1 |
| 255 | none | text | chunked-4 | no | decoded | unknown | bytes | - | 1 | 1 |
| 255 | signature:Observed("sps1") | signature:Observed("sps1") | chunked-3 | no | decoded | unknown | bytes | - | 1 | 1 |
| 255 | xml:ActionCoordinator__ActionCoordinatorData | xml:ActionCoordinator__ActionCoordinatorData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:BoatHullBlackList | xml:BoatHullBlackList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAimUpperBodyDataBlock | xml:CAimUpperBodyDataBlock | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimSceneAttachSlotSetManager | xml:CAnimSceneAttachSlotSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimalAnimationContexts | xml:CAnimalAnimationContexts | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAnimalAttackBehaviours | xml:CAnimalAttackBehaviours | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CAttachmentSlotData | xml:CAttachmentSlotData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBaitingInfo | xml:CBaitingInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBodyAnimConstraintInfoStateSetManager | xml:CBodyAnimConstraintInfoStateSetManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CBreakableVehicleDoorLockManagerData | xml:CBreakableVehicleDoorLockManagerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CClimbTuneMgr | xml:CClimbTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CCombatInfoMgr | xml:CCombatInfoMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CContentsOfWeatherXmlFile | xml:CContentsOfWeatherXmlFile | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CConversationDictionary | xml:CConversationDictionary | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CConversationList | xml:CConversationList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDiscoverableCollection | xml:CDiscoverableCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDoorInteractionDataList | xml:CDoorInteractionDataList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDrivingStyleCollection | xml:CDrivingStyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CDynamicScenarioManager | xml:CDynamicScenarioManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CEnergyConfigInfos | xml:CEnergyConfigInfos | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CEntityComponentLodManagerData | xml:CEntityComponentLodManagerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFallenSnowData | xml:CFallenSnowData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFiringPatternInfoManager | xml:CFiringPatternInfoManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFleeDecisionMakerData | xml:CFleeDecisionMakerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CFluidVesselManager | xml:CFluidVesselManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CGarageInitDataList | xml:CGarageInitDataList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CGraphicsDefinitionsData | xml:CGraphicsDefinitionsData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHazardNodes | xml:CHazardNodes | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHeadbobConditionManager | xml:CHeadbobConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CHealthConfigInfo | xml:CHealthConfigInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CIdlePreferenceManager | xml:CIdlePreferenceManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLadderMetadataManager | xml:CLadderMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLadderRailsMetadataManager | xml:CLadderRailsMetadataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CLassoDataManager | xml:CLassoDataManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMissions | xml:CMissions | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMoodConditionManager | xml:CMoodConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CMovieQualityVariationMap | xml:CMovieQualityVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CObjectComponentSetManager | xml:CObjectComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPairedPedDataBlock | xml:CPairedPedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CParkingSplines | xml:CParkingSplines | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedAccuracyManager | xml:CPedAccuracyManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedArmourMetaData | xml:CPedArmourMetaData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedBreathingTypes | xml:CPedBreathingTypes | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedComponentSetManager | xml:CPedComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedDensityScoringConfigMap | xml:CPedDensityScoringConfigMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedFormationInfoManager | xml:CPedFormationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedHeadbobSettingsManager | xml:CPedHeadbobSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedInventoryLoadOutManager | xml:CPedInventoryLoadOutManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMoodConditionTreesManager | xml:CPedMoodConditionTreesManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMoodSettingsManager | xml:CPedMoodSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedMotivationInfoManager | xml:CPedMotivationInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedScheduleInfoManager | xml:CPedScheduleInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedSpeedDataBlock | xml:CPedSpeedDataBlock | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedTimeWarpSettingsManager | xml:CPedTimeWarpSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPedVariationBodyTypeManager | xml:CPedVariationBodyTypeManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPersonaEnumValuesMap | xml:CPersonaEnumValuesMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CPlayerDiscoverableDataCollection | xml:CPlayerDiscoverableDataCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CProceduralInfo | xml:CProceduralInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScatteringTransmittance__FogVolumeListData | xml:CScatteringTransmittance__FogVolumeListData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScenarioPropDataManager | xml:CScenarioPropDataManager | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSceneTerrainAnalyzerMgrDataInstance | xml:CSceneTerrainAnalyzerMgrDataInstance | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CScenicViewManager | xml:CScenicViewManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSearchPointOfInterestRuleSet | xml:CSearchPointOfInterestRuleSet | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CSnowTrackData | xml:CSnowTrackData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CStandardPosesManager | xml:CStandardPosesManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTVPlaylistContainer | xml:CTVPlaylistContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTacticalAnalysisDistributionStore | xml:CTacticalAnalysisDistributionStore | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTaskDataInfoManager | xml:CTaskDataInfoManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTaskMoveLocalMovement__Tunables | xml:CTaskMoveLocalMovement__Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTrainConfigs | xml:CTrainConfigs | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CTyreDataSet | xml:CTyreDataSet | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CUpperBodyIdleConditionManager | xml:CUpperBodyIdleConditionManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CUpperBodyIdleSettingsManager | xml:CUpperBodyIdleSettingsManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleAIHandlingEntry | xml:CVehicleAIHandlingEntry | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleBaseRatingsAndEstimatesMap | xml:CVehicleBaseRatingsAndEstimatesMap | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleBoneOffsetsArray | xml:CVehicleBoneOffsetsArray | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleComponentSetManager | xml:CVehicleComponentSetManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehicleDistantLightData | xml:CVehicleDistantLightData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CVehiclePointsMeta | xml:CVehiclePointsMeta | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CWeaponActionHashToIndexMappings | xml:CWeaponActionHashToIndexMappings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Clock__Filter__Presets | xml:Clock__Filter__Presets | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Combat__GoalData__Store | xml:Combat__GoalData__Store | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Combat__Settings__ActionStore | xml:Combat__Settings__ActionStore | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Confront__StyleCollection | xml:Confront__StyleCollection | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CoverShadowTunables | xml:CoverShadowTunables | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:CustomClouds | xml:CustomClouds | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:DiffractionProfiles | xml:DiffractionProfiles | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:EnvironmentalWaterDisturbManager | xml:EnvironmentalWaterDisturbManager | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:FogVolumeProfileList | xml:FogVolumeProfileList | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GameShape__Data__LocationNameLoopkup | xml:GameShape__Data__LocationNameLoopkup | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GameShape__Data__ManagerSettings | xml:GameShape__Data__ManagerSettings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:GlintsProfiles | xml:GlintsProfiles | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:InteractionFoam_Tunables | xml:InteractionFoam_Tunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:InteriorGroups | xml:InteriorGroups | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LUTColorblindnessVariationMap | xml:LUTColorblindnessVariationMap | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LandingPageVideos | xml:LandingPageVideos | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LightAnimationPresets | xml:LightAnimationPresets | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:LostTargetSearch__Tunables | xml:LostTargetSearch__Tunables | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MainWaterTune | xml:MainWaterTune | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MapState__Data__Templates | xml:MapState__Data__Templates | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:MaterialDataList | xml:MaterialDataList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Mindset__CMindsetDictionary | xml:Mindset__CMindsetDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:ModelTagMappings | xml:ModelTagMappings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:ModelTags | xml:ModelTags | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Modular__SM__AIBehaviour__LockControllerConfig | xml:Modular__SM__AIBehaviour__LockControllerConfig | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:OceanSimPresets | xml:OceanSimPresets | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:OceanWaveCalmingCurves | xml:OceanWaveCalmingCurves | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PatchConstants | xml:PatchConstants | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PathingStyleData | xml:PathingStyleData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PedMotion__PedMotionData | xml:PedMotion__PedMotionData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PostFXSpline__Store | xml:PostFXSpline__Store | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:PromptInternal__PromptTunables | xml:PromptInternal__PromptTunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:RegionTintMap | xml:RegionTintMap | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Relationships__GroupsData | xml:Relationships__GroupsData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Respawn__MetaData | xml:Respawn__MetaData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:RumbleProfileList | xml:RumbleProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SMandatoryPacksData | xml:SMandatoryPacksData | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STPedMotionPredictionSetContainer | xml:STPedMotionPredictionSetContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STPedNavigationPredictiontPresetContainer | xml:STPedNavigationPredictiontPresetContainer | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:STS_Config | xml:STS_Config | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SoftBoundTuningList | xml:SoftBoundTuningList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:SpecialAbilityTagTargetsSettings | xml:SpecialAbilityTagTargetsSettings | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Sprinklers__RootData | xml:Sprinklers__RootData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:StudioConfigurationData | xml:StudioConfigurationData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Tactical__PointValidation__DataStore | xml:Tactical__PointValidation__DataStore | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TextureGridInfo | xml:TextureGridInfo | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:TyreProfileList | xml:TyreProfileList | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:VehicleFragImpulseFunction | xml:VehicleFragImpulseFunction | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WalkAndTalkProfileData | xml:WalkAndTalkProfileData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WaterTessellationSettings__AllAllowancesAndThresholds | xml:WaterTessellationSettings__AllAllowancesAndThresholds | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WeaponAnimations__ConfigData | xml:WeaponAnimations__ConfigData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:WeaponAnimations__FullbodyControllerData | xml:WeaponAnimations__FullbodyControllerData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:Witnesses__Informations | xml:Witnesses__Informations | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:aiNavIMapGroupData | xml:aiNavIMapGroupData | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:hrsSimTuneMgr | xml:hrsSimTuneMgr | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:naSpeechEventTypeBatchRequestParams | xml:naSpeechEventTypeBatchRequestParams | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__MediaDecoderSettings | xml:rage__MediaDecoderSettings | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__bgConfig | xml:rage__bgConfig | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__crRetarget__SolversTunables | xml:rage__crRetarget__SolversTunables | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__fragTuneStruct | xml:rage__fragTuneStruct | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__fwRetargetCoordinatorConfig | xml:rage__fwRetargetCoordinatorConfig | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:rage__phMBS_MaterialParamsDatabase_Def | xml:rage__phMBS_MaterialParamsDatabase_Def | chunked-3 | yes | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sCollisionEventScannerTuning | xml:sCollisionEventScannerTuning | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sPedDamageModifiers | xml:sPedDamageModifiers | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:sPedDistractionModifiers | xml:sPedDistractionModifiers | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |
| 255 | xml:time_data | xml:time_data | chunked-3 | no | decoded | verified | text | xml | 1 | 1 |

Samples of type 255 as `format:adat`:
- `audio.rpf!0!0`: 315,488 bytes, head `41444154010025ff020000004000000000000300a54329040000000018811d53`
- `audio.rpf!0!1`: 102,496 bytes, head `41444154010025ff020000004000000000000300a54329040000000028c8b652`
- `audio.rpf!0!2`: 92,256 bytes, head `41444154010025ff020000004000000000000300a5432904000000009340d4d4`
- `pack/shared_minigame000/shared_minigame000.rpf!7!0`: 589,856 bytes, head `41444154010021ff4d000000f60b00000000040008000b000f00130017001a00`
- `pack/shared_minigame000/shared_minigame000.rpf!7!1`: 1,027,712 bytes, head `41444154010021ff74000000741100000000030007000a000e00120015001800`
- `pack/shared_minigame000/shared_minigame000.rpf!7!2`: 80,416 bytes, head `41444154010021ff1c000000ac0400000000040008000c001000140018001c00`
- `pack/story000/story000.rpf!0!0`: 63,344 bytes, head `41444154010002ff010000004c000000c40087f12cf600400a0000364c000000`
- `pack/story000/story000.rpf!0!1`: 76,776 bytes, head `41444154010002ff010000004c000000024b2ae39c2801a0090000364c000000`
- `pack/story000/story000.rpf!0!2`: 36,912 bytes, head `41444154010002ff02000000880000008411d8eb8968ebef283d000001000036`
- `pack/story000_restofworld/story000_restofworld.rpf!3!0`: 146,048 bytes, head `41444154010002ff0600000078010000f65689e25c7f16e7bf3130e78cd21aeb`
- `pack/story000_restofworld/story000_restofworld.rpf!3!1`: 57,032 bytes, head `41444154010002ff03000000c4000000ab95dae2bcd658f705b2d1fbd44a0060`
- `pack/story000_restofworld/story000_restofworld.rpf!16!0`: 1,925,600 bytes, head `41444154010025ff070000007a0000000000030003000300030003000300ce13`

Samples of type 255 as `format:kb2`:
- `movies.rpf!0`: 1,866,836 bytes, head `4b42326e4c7c1c008c000000244b00008c00000000050000d00200001e000000`
- `movies.rpf!1`: 3,029,820 bytes, head `4b42326e343b2e002c010000f0e000002c010000d0020000000500001e000000`
- `movies.rpf!2`: 2,214,456 bytes, head `4b42326e30ca2100a60000001c5a0000a600000000050000d00200001e000000`
- `pack/core_restofworld/core_restofworld.rpf!12`: 177,458,460 bytes, head `4b42326e14cd930a88200000687b03008820000080070000380400001e000000`
- `pack/core_restofworld/core_restofworld.rpf!13`: 18,025,788 bytes, head `4b42326e340d1301da020000e81c0100da02000080070000380400001e000000`
- `pack/core_restofworld/core_restofworld.rpf!14`: 11,281,540 bytes, head `4b42326e7c24ac00c20100001c920100c201000080070000380400001e000000`
- `pack/story000/story000.rpf!441`: 8,086,068 bytes, head `4b42326e2c627b002c010000d0e600002c01000000080000d00200001e000000`
- `pack/story000/story000.rpf!442`: 6,043,564 bytes, head `4b42326ea4375c00c3010000f8e10000c3010000d0020000000500001e000000`
- `pack/story000/story000.rpf!443`: 1,942,064 bytes, head `4b42326e28a21d00d90000004c690100d900000080070000380400001e000000`
- `pack/story000_restofworld/story000_restofworld.rpf!21`: 5,700,272 bytes, head `4b42326ea8fa5600a9010000d8ce0000a9010000d0020000000500001e000000`
- `pack/story000_restofworld/story000_restofworld.rpf!22`: 64,438,264 bytes, head `4b42326ef03fd703780c0000ac250100780c000080070000380400001e000000`
- `pack/story000_restofworld/story000_restofworld.rpf!23`: 8,711,344 bytes, head `4b42326ea8ec84008b020000500c01008b020000d0020000000500001e000000`

Samples of type 255 as `xml:CDataFileMgr__ContentChangeSetDef`:
- `common.rpf!4`: 74,268 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!6`: 1,243 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!8`: 648 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`
- `pack/core_bvh4/core_bvh4.rpf!1281`: 157,888 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_bvh4/core_bvh4.rpf!1282`: 157,888 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_bvh4/core_bvh4.rpf!1283`: 157,888 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_licenses/core_licenses_data.rpf!1`: 763 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld/core_restofworld.rpf!10`: 771 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld/core_restofworld.rpf!11`: 2,018 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld/core_restofworld.rpf!17`: 1,412 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld001/core_restofworld001.rpf!2`: 777 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld001/core_restofworld001.rpf!3`: 961 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000/shared_minigame000.rpf!49`: 3,419 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000/shared_minigame000.rpf!50`: 1,018 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000/shared_minigame000.rpf!51`: 1,183 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!8`: 1,479 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!9`: 981 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!12`: 1,041 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000/story000.rpf!456`: 754 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000/story000.rpf!458`: 1,003 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000/story000.rpf!470`: 3,377 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_bvh4/story000_bvh4.rpf!0`: 800 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_bvh4/story000_bvh4.rpf!1`: 14,426 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_restofworld/story000_restofworld.rpf!18`: 772 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `binary:12000000`:
- `audio.rpf!14!2`: 71 bytes, head `1200000013000000ea885a04000000010000004d44a2a0040000000400000000`
- `audio.rpf!14!10`: 3,275,304 bytes, head `12000000f8002e00ea885a0401441d0c4312931280086210a00bcc14cb1b941c`
- `audio.rpf!14!12`: 71 bytes, head `1200000013000000ea885a04000000010000006693932a040000000400000000`
- `audio.rpf!14!7`: 1,136,793 bytes, head `14000000ade41000ea885a0403aaaaaaaa090000000600000002000000080700`
- `audio.rpf!14!13`: 521,572 bytes, head `1900000014210700ea885a0404aaaaaaaa000000000000000000803f04000000`
- `audio.rpf!14!4`: 17,964 bytes, head `1a0000008c3e0000ea885a0408000000aaaaaaaa000000000000000000000000`
- `audio.rpf!14!17`: 399,540 bytes, head `1a00000044f70400ea885a0403000000aaaaaaaa617564696f3a2f7366782f00`
- `audio.rpf!14!9`: 17,412 bytes, head `29000000d0350000ea885a0400a0aaaaaa00000044fd00005c5d000000000000`
- `audio.rpf!14!16`: 895,898 bytes, head `3d00000096980a00ea885a0403010000aa00000000ffffffffffffffff000100`
- `audio.rpf!14!3`: 19,947,076 bytes, head `45020000f4c4d300ea885a04cb0000000100cb000000020001cb0000000102cb`
- `audio.rpf!14!6`: 11,030,779 bytes, head `56000000f30e6d00ea885a0404aaaaaaaa00000002000000f6dc2b7e00000000`
- `audio.rpf!14!0`: 52 bytes, head `a600000004000000ea885a040400000000000000040000000000000000000000`
- `audio.rpf!14!15`: 15,574,463 bytes, head `a60000006f2e9200ea885a0431aaaaaaaa000031aaaaaaaa0500ec4786040000`
- `audio.rpf!14!1`: 5,242 bytes, head `414d425f53545245414d5f414e494d414c5f303100414d425f53545245414d5f`
- `audio.rpf!14!5`: 195,439 bytes, head `64726976657253657474696e67735f57617665526f6f74506174680064726976`
- `audio.rpf!14!8`: 522 bytes, head `42617365436f6d6d6f6e3a736f756e64735f636f6d6d6f6e3a536f756e64730d`
- `common.rpf!111`: 3,274,036 bytes, head `000000c0000000c0000000c0000000c0000000c0000000c0000000c0000000c0`
- `common.rpf!300`: 1,038,100 bytes, head `210300003bb86173fb5c57633bb86173fb5c576300fd3fbb6f9b5f9b479b3fbb`
- `common.rpf!332`: 48,588 bytes, head `50414d4801020000ed8cbc1b9000a400000050c6000018c6000097c30000a045`
- `common.rpf!117`: 117,176 bytes, head `636c6f7564732e737472617475732e6e6f6973655f776569676874732e6d6564`
- `common.rpf!151`: 47 bytes, head `505446585f4149525f524553495354414e434520312e300d0a47454e5f574154`
- `common.rpf!185`: 24,285 bytes, head `616c7068615265736f6c76652e66780d0a616d6269656e742e66780d0a616d62`
- `levels.rpf!326!0`: 15 bytes, head `464f5243455f454d5054595f525046`
- `levels.rpf!1220!0`: 15 bytes, head `464f5243455f454d5054595f525046`

Samples of type 255 as `xml:timecycle_modifier_data`:
- `common.rpf!20`: 46,064 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!26`: 113,019 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!30`: 19,545 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:rage__bgCrackType`:
- `common.rpf!48`: 4,624 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!52`: 4,609 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!54`: 1,398 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CVehiclePoints`:
- `common.rpf!18`: 370 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!25`: 592 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!43`: 1,907 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:timecycle_keyframe_data`:
- `common.rpf!13`: 170,803 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!15`: 391,626 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!22`: 391,706 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTuningFile`:
- `common.rpf!0`: 2,935 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!10`: 3,843 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!28`: 40,674 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CDataFileMgr__ContentChangeSetDef`:
- `common.rpf!2`: 694 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`
- `common.rpf!12`: 7,269 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`
- `common.rpf!14`: 1,274 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CDataFileMgr__ContentDef`:
- `common.rpf!211`: 9,399 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!321`: 4,827 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_bvh4/core_bvh4.rpf!1285`: 553 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `pack/core_licenses/core_licenses_data.rpf!3`: 455 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld/core_restofworld.rpf!29`: 1,640 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld001/core_restofworld001.rpf!5`: 638 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000/shared_minigame000.rpf!63`: 2,458 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!11`: 794 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000/story000.rpf!695`: 5,232 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_bvh4/story000_bvh4.rpf!3`: 622 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_restofworld/story000_restofworld.rpf!36`: 2,225 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CTuningFile`:
- `common.rpf!41`: 1,727 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!76`: 709 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!108`: 266 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:SSetupData`:
- `common.rpf!295`: 2,912 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_bvh4/core_bvh4.rpf!1284`: 472 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `pack/core_licenses/core_licenses_data.rpf!2`: 786 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld/core_restofworld.rpf!26`: 1,482 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/core_restofworld001/core_restofworld001.rpf!4`: 859 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000/shared_minigame000.rpf!60`: 1,561 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/shared_minigame000_bvh4/shared_minigame000_bvh4.rpf!10`: 885 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000/story000.rpf!674`: 2,267 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_bvh4/story000_bvh4.rpf!2`: 829 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `pack/story000_restofworld/story000_restofworld.rpf!34`: 1,470 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `text`:
- `common.rpf!45`: 23,668 bytes, head `3233330d0a330d0a3232372e36313633093230382e373139380d0a3232392e35`
- `common.rpf!204`: 26,704 bytes, head `3230300d0a360d0a31302e38353439093436322e343938340d0a302e30303030`
- `common.rpf!208`: 45,781 bytes, head `3335300d0a370d0a3233332e30393434093235382e313930350d0a3231382e33`

Samples of type 255 as `xml:WaveData`:
- `common.rpf!17`: 747 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!169`: 957 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!271`: 6,855 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `format:edup`:
- `pack/core_restofworld/core_restofworld.rpf!15`: 1,548 bytes, head `454455502100000093fe3be87ed4b60243fb4dd2543668530552cb8482016604`
- `pack/core_restofworld001/core_restofworld001.rpf!1`: 28 bytes, head `45445550000000001000000091616df07a5df6d6aa87f0fde046897c`
- `pack/shared_minigame000/shared_minigame000.rpf!53`: 236 bytes, head `4544555004000000947475e857e00412a34145a3e1ff7584666bda319b746a87`
- `pack/story000/story000.rpf!532`: 28 bytes, head `45445550000000001000000091616df07a5df6d6aa87f0fde046897c`
- `textures.rpf!20`: 965,964 bytes, head `4544555017440000e213c93376ba0200559b36b0fba88dcc6536f8da62060400`

Samples of type 255 as `xml:CDamageDataManager`:
- `common.rpf!148`: 12,498 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!216`: 104,082 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!236`: 257,008 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:GridAtlasInfo`:
- `common.rpf!23`: 1,040 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!40`: 1,044 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!183`: 1,078 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CCoverProcessorTuning`:
- `common.rpf!16`: 11,554 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`
- `common.rpf!74`: 11,422 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!242`: 11,404 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `format:psin`:
- `appdata0.rpf!0`: 976 bytes, head `5053494e000000c0100000002c000000aaaaaaaaaaaaaaaa98a6318c58000000`
- `appdata0.rpf!1`: 19,392 bytes, head `5053494e00003cd0b4121b23f0030000aaaaaaaaaaaaaaaa65878f2480000000`

Samples of type 255 as `signature:Observed("mhiu")`:
- `common.rpf!243`: 1,189,171 bytes, head `4d484955010000080008000000204bc600a00cc6000048c200c0da4500e02b46`
- `common.rpf!316`: 1,210,476 bytes, head `4d484955010000080008000000204bc600a00cc6000048c200c0da4500e02b46`

Samples of type 255 as `signature:Observed("sgd5")`:
- `shaders.rpf!1`: 3,086,891 bytes, head `53474435d63efb3edcf25d0903000000f800000010d13697d046ab5e1c00001a`
- `shaders.rpf!2`: 271,048,467 bytes, head `53474435b3728ba0c25d55602100000040080000f0898472ebf2c1c6050100eb`

Samples of type 255 as `xml:CVehiclePerformanceMaps`:
- `common.rpf!129`: 16,040 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!391`: 117,808 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:ShoreWavePlacementData`:
- `common.rpf!373`: 2,369,981 bytes, head `3c3f786d6c2076657273696f6e3d27312e302720656e636f64696e673d277574`
- `pack/shared_minigame000/shared_minigame000.rpf!66`: 33,393 bytes, head `3c3f786d6c2076657273696f6e3d27312e302720656e636f64696e673d277574`

Samples of type 255 as `xml:VehicleControlsInfo`:
- `common.rpf!145`: 52,854 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!286`: 26,632 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:unvalidated`:
- `common.rpf!314`: 14,262,150 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`
- `common.rpf!385`: 4,283,195 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `text`:
- `levels.rpf!1091!0`: 15 bytes, head `464f5243455f454d5054595f525046`

Samples of type 255 as `signature:Observed("sps1")`:
- `common.rpf!78`: 43,791 bytes, head `535053315a0300001b315374727563747572652f62655f7374616e646172642e`

Samples of type 255 as `xml:ActionCoordinator__ActionCoordinatorData`:
- `common.rpf!382`: 33,008 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:BoatHullBlackList`:
- `common.rpf!223`: 297 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CAimUpperBodyDataBlock`:
- `common.rpf!136`: 67,349 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CAnimSceneAttachSlotSetManager`:
- `common.rpf!340`: 10,632 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CAnimalAnimationContexts`:
- `common.rpf!160`: 10,013 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CAnimalAttackBehaviours`:
- `common.rpf!397`: 55,388 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CAttachmentSlotData`:
- `common.rpf!339`: 11,475 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CBaitingInfo`:
- `common.rpf!203`: 2,717 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CBodyAnimConstraintInfoStateSetManager`:
- `common.rpf!410`: 44,462 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CBreakableVehicleDoorLockManagerData`:
- `common.rpf!88`: 10,478 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CClimbTuneMgr`:
- `common.rpf!402`: 54,137 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CCombatInfoMgr`:
- `common.rpf!220`: 237,621 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CContentsOfWeatherXmlFile`:
- `common.rpf!144`: 212,258 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CConversationDictionary`:
- `common.rpf!304`: 179,493 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CConversationList`:
- `common.rpf!19`: 70,507 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CDiscoverableCollection`:
- `common.rpf!59`: 64,852 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CDoorInteractionDataList`:
- `common.rpf!259`: 404,957 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CDrivingStyleCollection`:
- `common.rpf!32`: 82,329 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CDynamicScenarioManager`:
- `common.rpf!270`: 10,533 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CEnergyConfigInfos`:
- `common.rpf!42`: 160,706 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CEntityComponentLodManagerData`:
- `common.rpf!180`: 5,007 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CFallenSnowData`:
- `common.rpf!57`: 5,278 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CFiringPatternInfoManager`:
- `common.rpf!356`: 273,776 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CFleeDecisionMakerData`:
- `common.rpf!161`: 17,561 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CFluidVesselManager`:
- `common.rpf!80`: 13,325 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CGarageInitDataList`:
- `common.rpf!112`: 102 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CGraphicsDefinitionsData`:
- `common.rpf!5`: 121,460 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CHazardNodes`:
- `common.rpf!176`: 23,517 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CHeadbobConditionManager`:
- `common.rpf!292`: 16,610 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CHealthConfigInfo`:
- `common.rpf!195`: 1,308 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CIdlePreferenceManager`:
- `common.rpf!247`: 1,005 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CLadderMetadataManager`:
- `common.rpf!406`: 6,996 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CLadderRailsMetadataManager`:
- `common.rpf!158`: 1,086 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CLassoDataManager`:
- `common.rpf!91`: 126,639 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CMissions`:
- `common.rpf!267`: 33,563 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CMoodConditionManager`:
- `common.rpf!331`: 122 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CMovieQualityVariationMap`:
- `common.rpf!99`: 394 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CObjectComponentSetManager`:
- `common.rpf!351`: 319 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPairedPedDataBlock`:
- `common.rpf!237`: 10,011 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CParkingSplines`:
- `common.rpf!103`: 21,009 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedAccuracyManager`:
- `common.rpf!261`: 8,347 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedArmourMetaData`:
- `common.rpf!162`: 7,006 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CPedBreathingTypes`:
- `common.rpf!346`: 5,005 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedComponentSetManager`:
- `common.rpf!130`: 33,770 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedDensityScoringConfigMap`:
- `common.rpf!375`: 1,473 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedFormationInfoManager`:
- `common.rpf!246`: 18,748 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedHeadbobSettingsManager`:
- `common.rpf!306`: 88,190 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CPedInventoryLoadOutManager`:
- `common.rpf!307`: 411,101 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CPedMoodConditionTreesManager`:
- `common.rpf!97`: 209 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CPedMoodSettingsManager`:
- `common.rpf!348`: 266 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedMotivationInfoManager`:
- `common.rpf!330`: 32,388 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedScheduleInfoManager`:
- `common.rpf!413`: 784,294 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedSpeedDataBlock`:
- `common.rpf!318`: 86,390 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPedTimeWarpSettingsManager`:
- `common.rpf!293`: 6,160 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CPedVariationBodyTypeManager`:
- `common.rpf!263`: 77,462 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CPersonaEnumValuesMap`:
- `common.rpf!33`: 1,900 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CPlayerDiscoverableDataCollection`:
- `common.rpf!73`: 35,897 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CProceduralInfo`:
- `common.rpf!381`: 20,701 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CScatteringTransmittance__FogVolumeListData`:
- `common.rpf!333`: 28,820 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CScenarioPropDataManager`:
- `common.rpf!287`: 12,330 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CSceneTerrainAnalyzerMgrDataInstance`:
- `common.rpf!55`: 110,723 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CScenicViewManager`:
- `common.rpf!157`: 7,327 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CSearchPointOfInterestRuleSet`:
- `common.rpf!167`: 34,987 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CSnowTrackData`:
- `common.rpf!46`: 36,522 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CStandardPosesManager`:
- `common.rpf!11`: 16,161 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTVPlaylistContainer`:
- `common.rpf!118`: 537 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTacticalAnalysisDistributionStore`:
- `common.rpf!266`: 22,913 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTaskDataInfoManager`:
- `common.rpf!335`: 192,988 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTaskMoveLocalMovement__Tunables`:
- `common.rpf!84`: 64,494 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CTrainConfigs`:
- `common.rpf!89`: 125,494 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CTyreDataSet`:
- `common.rpf!226`: 76,685 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CUpperBodyIdleConditionManager`:
- `common.rpf!366`: 13,435 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CUpperBodyIdleSettingsManager`:
- `common.rpf!380`: 3,439 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehicleAIHandlingEntry`:
- `common.rpf!127`: 9,749 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehicleBaseRatingsAndEstimatesMap`:
- `common.rpf!139`: 352,136 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehicleBoneOffsetsArray`:
- `common.rpf!359`: 20,688 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehicleComponentSetManager`:
- `common.rpf!159`: 15,562 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehicleDistantLightData`:
- `common.rpf!1`: 410,897 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CVehiclePointsMeta`:
- `common.rpf!265`: 2,555 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:CWeaponActionHashToIndexMappings`:
- `common.rpf!70`: 39,789 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Clock__Filter__Presets`:
- `common.rpf!94`: 12,086 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Combat__GoalData__Store`:
- `common.rpf!225`: 4,550 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Combat__Settings__ActionStore`:
- `common.rpf!152`: 10,172 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Confront__StyleCollection`:
- `common.rpf!258`: 59,107 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:CoverShadowTunables`:
- `common.rpf!107`: 828 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:CustomClouds`:
- `common.rpf!278`: 396,586 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:DiffractionProfiles`:
- `common.rpf!65`: 6,447 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:EnvironmentalWaterDisturbManager`:
- `common.rpf!62`: 148 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e67203d2022`

Samples of type 255 as `xml:FogVolumeProfileList`:
- `common.rpf!154`: 18,887 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:GameShape__Data__LocationNameLoopkup`:
- `common.rpf!178`: 671,393 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:GameShape__Data__ManagerSettings`:
- `common.rpf!44`: 9,898 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:GlintsProfiles`:
- `common.rpf!405`: 9,237 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:InteractionFoam_Tunables`:
- `common.rpf!29`: 687 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:InteriorGroups`:
- `common.rpf!3`: 13,677 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:LUTColorblindnessVariationMap`:
- `common.rpf!213`: 126 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:LandingPageVideos`:
- `common.rpf!92`: 644 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:LightAnimationPresets`:
- `common.rpf!219`: 231 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:LostTargetSearch__Tunables`:
- `common.rpf!69`: 848 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:MainWaterTune`:
- `common.rpf!164`: 865 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:MapState__Data__Templates`:
- `common.rpf!319`: 131 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:MaterialDataList`:
- `common.rpf!371`: 395,211 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Mindset__CMindsetDictionary`:
- `common.rpf!96`: 42,015 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:ModelTagMappings`:
- `common.rpf!324`: 248,855 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:ModelTags`:
- `common.rpf!241`: 7,276 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Modular__SM__AIBehaviour__LockControllerConfig`:
- `common.rpf!61`: 547 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Modular__SM__AmbientCompanion__Profile__CBuddyMindsetProfileDictionary`:
- `common.rpf!50`: 9,945 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:OceanSimPresets`:
- `common.rpf!7`: 12,430 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:OceanWaveCalmingCurves`:
- `common.rpf!250`: 1,030 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:PatchConstants`:
- `common.rpf!409`: 17,574 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:PathingStyleData`:
- `common.rpf!72`: 5,993 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:PedMotion__PedMotionData`:
- `common.rpf!363`: 1,182 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:PostFXSpline__Store`:
- `common.rpf!312`: 87 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:PromptInternal__PromptTunables`:
- `common.rpf!194`: 3,199 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:RegionTintMap`:
- `common.rpf!395`: 676 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Relationships__GroupsData`:
- `common.rpf!370`: 35,555 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Respawn__MetaData`:
- `common.rpf!249`: 13,231 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:RumbleProfileList`:
- `common.rpf!123`: 7,830 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:SMandatoryPacksData`:
- `common.rpf!21`: 100 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:STPedMotionPredictionSetContainer`:
- `common.rpf!155`: 50,327 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:STPedNavigationPredictiontPresetContainer`:
- `common.rpf!274`: 92,999 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:STS_Config`:
- `common.rpf!79`: 7,689 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:SoftBoundTuningList`:
- `common.rpf!146`: 3,867 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:SpecialAbilityTagTargetsSettings`:
- `common.rpf!285`: 588 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Sprinklers__RootData`:
- `common.rpf!378`: 12,534 bytes, head `3c537072696e6b6c6572735f5f526f6f74446174613e0d0a093c54797065733e`

Samples of type 255 as `xml:StudioConfigurationData`:
- `common.rpf!137`: 5,913 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:Tactical__PointValidation__DataStore`:
- `common.rpf!147`: 14,892 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:TargetScoring__ProfileDataStore_t_PedAccuracy__ScoringFactor__Enum`:
- `common.rpf!399`: 41,460 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:TargetScoring__ProfileDataStore_t_PedTargetScoring__ScoringFactor__Enum`:
- `common.rpf!56`: 17,555 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:TextureGridInfo`:
- `common.rpf!296`: 409 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:TyreProfileList`:
- `common.rpf!387`: 6,790 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:VehicleFragImpulseFunction`:
- `common.rpf!119`: 1,506 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:WalkAndTalkProfileData`:
- `common.rpf!207`: 15,441 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:WaterTessellationSettings__AllAllowancesAndThresholds`:
- `common.rpf!85`: 17,147 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d227574`

Samples of type 255 as `xml:WeaponAnimations__ConfigData`:
- `common.rpf!218`: 1,733 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:WeaponAnimations__FullbodyControllerData`:
- `common.rpf!187`: 21,281 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:Witnesses__Informations`:
- `common.rpf!386`: 144,572 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:aiNavIMapGroupData`:
- `common.rpf!282`: 5,838 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:hrsSimTuneMgr`:
- `common.rpf!276`: 1,811 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:naSpeechEventTypeBatchRequestParams`:
- `common.rpf!51`: 12,143 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:rage__MediaDecoderSettings`:
- `common.rpf!408`: 417 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:rage__bgConfig`:
- `common.rpf!149`: 3,463 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:rage__crRetarget__SolversTunables`:
- `common.rpf!352`: 19,991 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:rage__fragTuneStruct`:
- `common.rpf!364`: 224,062 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:rage__fwRetargetCoordinatorConfig`:
- `common.rpf!227`: 680 bytes, head `efbbbf3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d`

Samples of type 255 as `xml:rage__phMBS_MaterialParamsDatabase_Def`:
- `common.rpf!199`: 31,204 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:sCollisionEventScannerTuning`:
- `common.rpf!66`: 10,400 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:sPedDamageModifiers`:
- `common.rpf!166`: 2,717 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:sPedDistractionModifiers`:
- `common.rpf!105`: 3,473 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

Samples of type 255 as `xml:time_data`:
- `common.rpf!303`: 1,370 bytes, head `3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554`

