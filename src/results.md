# Golden data
---
- Data information:
datasize: 1204
formattedIncorrectly: 185
ProcentageWellFormated:  % 0.8463455149501661
WellFormatedDatasize:   1019
---
- Does folioLabel == prover9Label?
provenCorrectly out of well formated: % 0.6712463199214916
correctly proven data out of all:  % 0.5681063122923588
correctly proven data count:   684 <- Gold data set count
---
# FINAL
## Experiment 1: FOL conclusion generation
Gemini
=== Label check ===
---
- Data information:
datasize: 683
formattedIncorrectly: 66
ProcentageWellFormated:  % 0.9033674963396779
WellFormatedDatasize:   617
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.9724473257698542
correctly proven data out of all:  % 0.8784773060029283
correctly proven data count:   600
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.8703403565640194
correctly proven data out of all:  % 0.7862371888726208
correctly proven data count:   537

ChatGPT
Bad format counts not the same??
14 15
=== Label check ===
---
- Data information:
datasize: 684
formattedIncorrectly: 15
ProcentageWellFormated:  % 0.9780701754385965
WellFormatedDatasize:   669
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.9237668161434978
correctly proven data out of all:  % 0.9035087719298246
correctly proven data count:   618
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.7877428998505231
correctly proven data out of all:  % 0.77046783625731
correctly proven data count:   527


## Experiment 2: FOL premises + conclusion generation
Gemini
Bad format counts not the same??
13 14
=== Label check ===
---
- Data information:
datasize: 682
formattedIncorrectly: 14
ProcentageWellFormated:  % 0.9794721407624634
WellFormatedDatasize:   668
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.5688622754491018
correctly proven data out of all:  % 0.5571847507331378
correctly proven data count:   380
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.19161676646706588
correctly proven data out of all:  % 0.187683284457478
correctly proven data count:   128

ChatGPT
Bad format counts not the same??
16 18
=== Label check ===
---
- Data information:
datasize: 683
formattedIncorrectly: 18
ProcentageWellFormated:  % 0.9736456808199122
WellFormatedDatasize:   665
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.6135338345864662
correctly proven data out of all:  % 0.5973645680819912
correctly proven data count:   408
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.26917293233082706
correctly proven data out of all:  % 0.26207906295754024
correctly proven data count:   179

## exp 2
Experiment 2: FOL premises + conclusion generation
Gemini
Bad format counts not the same??
13 14 8
---
- Data information:
datasize: 682
formattedIncorrectly: 14
ProcentageWellFormated:  % 0.9794721407624634
WellFormatedDatasize:   668
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.5688622754491018
correctly proven data out of all:  % 0.5571847507331378
correctly proven data count:   380
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.19161676646706588
correctly proven data out of all:  % 0.187683284457478
correctly proven data count:   128
---
- Does P => LLMP?
provenCorrectly out of well formated:  % 0.0658682634730539
correctly proven data out of all:  % 0.06451612903225806
correctly proven data count:   44
---
- Does dfPrem+Concl <-> llmPrem+Concl?
provenCorrectly out of well formated:  % 0.5583832335329342
correctly proven data out of all:  % 0.5469208211143695
correctly proven data count:   373
---
- Does dfPrem+dfConcl <-> llmPrem+llmConcl?
provenCorrectly out of well formated:  % 0.8922155688622755
correctly proven data out of all:  % 0.873900293255132
correctly proven data count:   596

ChatGPT
Bad format counts not the same??
16 18 13
---
- Data information:
datasize: 683
formattedIncorrectly: 18
ProcentageWellFormated:  % 0.9736456808199122
WellFormatedDatasize:   665
---
- Does dfLabel == llmLabel?
provenCorrectly out of well formated:  % 0.6135338345864662
correctly proven data out of all:  % 0.5973645680819912
correctly proven data count:   408
---
- Does dfConcl <-> llmConcl?
provenCorrectly out of well formated:  % 0.26917293233082706
correctly proven data out of all:  % 0.26207906295754024
correctly proven data count:   179
---
- Does P => LLMP?
provenCorrectly out of well formated:  % 0.06616541353383458
correctly proven data out of all:  % 0.06442166910688141
correctly proven data count:   44
---
- Does dfPrem+Concl <-> llmPrem+Concl?
provenCorrectly out of well formated:  % 0.5548872180451128
correctly proven data out of all:  % 0.5402635431918009
correctly proven data count:   369
---
- Does dfPrem+dfConcl <-> llmPrem+llmConcl?
provenCorrectly out of well formated:  % 0.7984962406015037
correctly proven data out of all:  % 0.7774524158125915
correctly proven data count:   531