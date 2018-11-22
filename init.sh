mkdir temp
cd temp
wget https://oscdl.ipa.go.jp/IPAexfont/ipaexg00201.zip
unzip ipaexg00201.zip
cp ipaexg00201/ipaexg.ttf ../font
cd ../
rm -rf temp
