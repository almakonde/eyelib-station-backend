# Upgrade procedure

## **v1.1.1** migration from v1.1

### **Update TwinCAT/TwinSAFE solution**
Connect you development laptop to Beckhoff via Visual Studio and do:
> 1. Checkout the corresponding version of _gen2-station-twincat_ project on your laptop
> 2. Activate both TwinCAT and TwinSAFE solutions
> 3. After restart, check for ```PS1_DRV_TBL_X```, ```PS1_DRV_TBL_Y```, ```PS1_DRV_CR``` and ```PS_AI``` if the Startup parameters are set up on their _80xx_ addresses


### **Update the code base**
For all nodes with high automations do:
> 1. Stop the corresponding automation
> 2. Backup the previous version of automation
> 3. Checkout the corresponding version of automation
> 4. Remove _.venv_ folder and _poetry.lock_ file
> 5. Run ```poetry install```

For Beckhoff:
> 1. Replace the  _static_ folder with the corresponding  _gen2-station-frontend_ generated one
> 2. On the station's xml please add the following tags under the ```<PS1 type="element">``` node: 
```
<StationHeight type="element">
    <length_mm type="float">702.0</length_mm>
    <offset_mm type="float">1100.0</offset_mm>            
    <tolerence_mm type="float">1.5</tolerence_mm>
    <encoder_min type="int">490</encoder_min>
    <encoder_max type="int">9360</encoder_max>
</StationHeight>
```
> 3. To set up the ```encoder_min``` and ```encoder_max``` values move the station to the lowest and higst position and store the corresponding values obtained on ```PS_AI (EL3121) -> AI Standars -> Value``` while connecting to TwinCAT


### **Update configuration**
For REVO:
> 1. Unselect _Placing a patinet head_ the from _Sounds_ configuration of SOCT