# APPCH Corpus
The **APPCH Corpus** (**A**pplication **P**rivacy **P**olicies in **Ch**inese) is a collection of application privacy policies (i.e., in natural language) with annotations, which reveals privacy information collection practice through **nine dangerous Android PERMISSIONs**.

| PERMISSION Group | PERMSSIONs                                                   | LABEL |
| ---------------- | ------------------------------------------------------------ | ----- |
| CALENDAR         | READ_CALENDAR、WRITE_CALENDAR                                | CAL   |
| CAMERA           | CAMERA                                                       | CAM   |
| CONTACTS         | READ_CONTACTS、WRITE_CONTACTS、GET_ACCOUNTS                  | CON   |
| LOCATION         | ACCESS_FINE_LOCATION、ACCESS_COARSE_LOCATION                 | LOC   |
| MICROPHONE       | RECORD_AUDIO                                                 | MIC   |
| PHONE            | READ_PHONE_STATE、CALL_PHONE、READ_CALL_LOG、<br/>WRITE_CALL_LOG、ADD_VOICEMAIL、USE_SIP、<br/>PROCESS_OUTGOING_CALLS | PHO   |
| SENSORS          | BODY_SENSORS                                                 | SEN   |
| SMS              | SEND_SMS、RECEIVE_SMS、READ_SMS、<br/>RECEIVE_WAP_PUSH、RECEIVE_MMS | SMS   |
| STORAGE          | READ_EXTERNAL_STORAGE、WRITE_EXTERNAL_STORAGE                | STO   |

- In manual annotation sets, each privacy policy was read and annotated by three annotators from Cyber Engneering School. By manual annotation, we got **98 labeled policies** and a dictionary of **678 data practice phrases**.


- Based on the above permission phrase dictionary, we made use of the **BMM** **(Bidirectional Maximum Matching)** algorithm for automatic annotation to expand the size of the corpus. 


- Finally,  APPCH Copus contained **1058 privacy policies** and **948K dangerous permission phrases**. We can build train/dev/test datasets based APPCH and then train NER(Named Entity Recognition) model to **extract data practice** from privacy policy.




The dataset is made available for research, teaching, and scholarship purposes only. You can find raw corpus in "spider" and labeled corpus in "annotations".

Special thanks to: [YEDDA]：https://github.com/jiesutd/YEDDA

