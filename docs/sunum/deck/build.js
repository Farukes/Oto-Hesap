// 3 dakikalık online sunum destesi (6 slayt: Proje Adı · Problem · Çözüm ×3 · Ekip).
// Çalıştır:  cd docs/sunum/deck && npm i && node build.js   → ../OtoHesap-3dk.pptx
// Telegram telefon görüntüsü varsa docs/img/telegram-telefon.png olarak kaydet; slayt 5'e otomatik girer.
const path=require("path"),fs=require("fs"),PptxGenJS=require("pptxgenjs");
const IMG=path.join(__dirname,"..","..","img"), OUT=path.join(__dirname,"..","OtoHesap-3dk.pptx");
const NAVY="0F2A3C",GREEN="1C8C6E",MINT="EAF5F1",WHITE="FFFFFF",INK="12303F",MUTED="4A6270",ON_DARK="C9DEE6",MB="7FD9BC",LINE="D3E4DD",RED="C0392B",PALE="F6FBF9";
const F="Arial",W=13.333,H=7.5,M=0.8;
const pptx=new PptxGenJS();pptx.layout="LAYOUT_WIDE";pptx.title="OtoHesap — 14 Eylül 2026";
const T=(s,t,o)=>s.addText(t,Object.assign({fontFace:F,isTextBox:true,margin:0},o));
const card=(s,x,y,w,h,fill,line)=>s.addShape("roundRect",{x,y,w,h,rectRadius:0.12,fill:{color:fill},line:line?{color:line,width:1}:{type:"none"}});
const img=(s,name,x,y,w,h,mode)=>{s.addImage({path:path.join(IMG,name),x,y,w,h,sizing:{type:mode||"contain",w,h}});s.addShape("rect",{x,y,w,h,fill:{type:"none"},line:{color:LINE,width:1}});};
const header=(s,title,kicker,size)=>{s.background={color:PALE};
  T(s,title,{x:M,y:0.55,w:9.6,h:0.9,fontSize:size||40,bold:true,color:NAVY});
  s.addShape("rect",{x:M,y:1.5,w:1.2,h:0.08,fill:{color:GREEN},line:{type:"none"}});
  if(kicker)T(s,kicker,{x:10.2,y:0.75,w:W-10.2-M,h:0.5,fontSize:16,color:MUTED,align:"right"});
  s.addImage({path:path.join(IMG,"logo.png"),x:W-M-0.38,y:H-0.62,w:0.38,h:0.38});
  T(s,"OtoHesap · TeknoKampüs Arena · 14 Eylül 2026",{x:M,y:H-0.55,w:8,h:0.3,fontSize:10,color:"8AA0AB"});};
const label=(s,t,x,y,w,color)=>T(s,t,{x,y,w,h:0.35,fontSize:13,bold:true,color});

// 1 · Proje Adı
{const s=pptx.addSlide();s.background={color:NAVY};
 T(s,"PROJE ADI",{x:M,y:0.7,w:6,h:0.4,fontSize:14,color:MB,bold:true,charSpacing:4});
 s.addImage({path:path.join(IMG,"logo.png"),x:M,y:1.75,w:1.7,h:1.7});
 T(s,"OtoHesap",{x:M+2.0,y:1.45,w:10,h:1.9,fontSize:88,bold:true,color:WHITE});
 T(s,"Küçük işletmeler için gelir-gider ve stok takibi",{x:M,y:3.85,w:11.7,h:0.8,fontSize:30,color:MB});
 T(s,"Ne kazandım, ne harcadım, stokta ne bitiyor? Türkçe sorun, cevabı alın.",{x:M,y:4.65,w:11.7,h:0.6,fontSize:19,color:ON_DARK});
 T(s,"Kutay Yıldırım   ·   Muratcan Ateş   ·   Ömer Faruk Eskitürk",{x:M,y:5.9,w:W-2*M,h:0.5,fontSize:18,color:WHITE,bold:true});
 T(s,"Medeniyet Teknopark · TeknoKampüs Arena · 14 Eylül 2026",{x:M,y:6.45,w:W-2*M,h:0.4,fontSize:13,color:ON_DARK});
 s.addNotes("0:00–0:20. Adı söyle, tek cümle: küçük işletme için gelir-gider ve stok; Türkçe soruyla cevap; stok azalınca onaylı sipariş.");}

// 2 · Problem
{const s=pptx.addSlide();header(s,"Problem","Küçük işletme çok, zamanı az");
 card(s,M,1.95,8.15,3.55,WHITE,LINE);
 T(s,"KOBİ'lerin Türkiye ekonomisindeki payı",{x:M+0.3,y:2.08,w:7.5,h:0.45,fontSize:17,bold:true,color:INK});
 s.addImage({path:path.join(IMG,"tuik-grafik.png"),x:M+0.25,y:2.55,w:7.65,h:2.44});
 T(s,"Kaynak: TÜİK, Küçük ve Orta Büyüklükteki Girişim İstatistikleri, 2024",{x:M+0.3,y:5.05,w:7.5,h:0.35,fontSize:10,color:MUTED,italic:true});
 T(s,"3,9 milyon",{x:9.2,y:2.0,w:3.4,h:0.85,fontSize:40,bold:true,color:GREEN});
 T(s,"KOBİ",{x:9.2,y:2.85,w:3.4,h:0.55,fontSize:26,bold:true,color:INK});
 T(s,"Türkiye'deki her 100 işletmeden 99'u KOBİ.\n\nHer 3 KOBİ'den 1'i ticaret yapıyor: mal alıyor, satıyor, stok tutuyor.",{x:9.2,y:3.5,w:3.35,h:1.9,fontSize:15,color:MUTED,valign:"top"});
 ["Rapor için Excel'le boğuşuyor","Stoğun bittiğini müşteri sorunca fark ediyor","Basit bir sorunun cevabı için menülerde dolaşıyor"].forEach((p,i)=>{const w=(W-2*M-0.5)/3,x=M+i*(w+0.25);
  card(s,x,5.75,w,0.85,WHITE,LINE);s.addShape("ellipse",{x:x+0.25,y:5.99,w:0.36,h:0.36,fill:{color:RED},line:{type:"none"}});
  T(s,p,{x:x+0.75,y:5.75,w:w-0.9,h:0.85,fontSize:14,bold:true,color:INK,valign:"middle"});});
 s.addNotes("0:20–0:50. Her 100 işletmeden 99'u KOBİ; 3,9 milyon. İstihdamın %68'i, cironun %44'ü. Her 3 KOBİ'den 1'i ticarette: alıyor, satıyor, stok tutuyor. Günlük dert: Excel, geç fark edilen stok, menülerde dolaşma.");}

// 3 · Çözüm · Tek ekranda gelir, gider, stok
{const s=pptx.addSlide();header(s,"Tek ekranda gelir, gider, stok","Çözüm",36);
 label(s,"OtoHesap · Genel Bakış ekranı",M,1.55,6,GREEN);
 img(s,"genel-bakis.png",M,1.95,7.6,4.75);
 const cx=8.75,cw=W-M-cx;
 [["Bu ay ne kazandım, ne harcadım?","Gelir, gider ve aradaki fark tek bakışta. Ay, çeyrek veya yarıyıl seçilir."],["Stokta ne bitiyor?","Kritik seviyeye inen ürünleri sistem kendisi söyler; siz aramazsınız."],["Gidişat nasıl?","Aylık gelir-gider grafiği. Bir giderde sıçrama olunca uyarır."]].forEach((c,i)=>{const y=1.95+i*1.62;
  card(s,cx,y,cw,1.4,WHITE,LINE);T(s,c[0],{x:cx+0.25,y:y+0.15,w:cw-0.5,h:0.45,fontSize:17,bold:true,color:GREEN});T(s,c[1],{x:cx+0.25,y:y+0.6,w:cw-0.5,h:0.75,fontSize:13,color:MUTED,valign:"top"});});
 s.addNotes("0:50–1:20. Birincisi: gelir, gider, fark ve kritik ürün tek ekranda. Sistem kendisi uyarıyor: iki ürün kritik stokta, reklam gideri artmış.");}

// 4 · Çözüm · Türkçe sor, cevabı al
{const s=pptx.addSlide();header(s,"Türkçe sor, cevabı al","Çözüm");
 const iy=1.95,ih=3.47,iw=5.55,rx=W-M-iw;
 label(s,"Bugün: cevabı Excel'de arıyorsunuz",M,1.55,iw,RED);
 s.addImage({path:path.join(IMG,"excel-karmasa.png"),x:M,y:iy,w:iw,h:ih,sizing:{type:"cover",w:iw,h:ih}});
 s.addShape("rect",{x:M,y:iy,w:iw,h:ih,fill:{type:"none"},line:{color:LINE,width:1}});
 label(s,"OtoHesap: \"En çok kazancım hangi üründen?\"",rx,1.55,iw,GREEN);
 img(s,"asistan-sade.png",rx,iy,iw,ih);
 s.addShape("ellipse",{x:6.3,y:3.3,w:0.75,h:0.75,fill:{color:GREEN},line:{type:"none"}});
 T(s,"➜",{x:6.3,y:3.3,w:0.75,h:0.75,fontSize:26,bold:true,color:WHITE,align:"center",valign:"middle"});
 ["Cevap kendi verinizden gelir, uydurma değil","Yapay zekâ veriyi sadece okur, değiştiremez","Şüpheli sorgu çalışmaz, uyarı verir"].forEach((c,i)=>{const w=(W-2*M-0.4)/3,x=M+i*(w+0.2);
  card(s,x,5.7,w,0.7,WHITE,LINE);T(s,c,{x:x+0.15,y:5.7,w:w-0.3,h:0.7,fontSize:14,bold:true,color:GREEN,align:"center",valign:"middle"});});
 T(s,"Merak eden, arkadaki sorguyu tek tıkla görebilir.",{x:M,y:6.5,w:W-2*M,h:0.35,fontSize:11,color:MUTED,italic:true,align:"center"});
 s.addNotes("1:20–1:55. Solda bugünkü hâl, sağda OtoHesap. Soruyu Türkçe yazıyorsunuz; cevap kendi verinizden geliyor, uydurma değil. Yapay zekâ veriyi sadece okur; şüpheli sorgu çalışmaz, uyarı verir. Cevap: Powerbank.");}

// 5 · Çözüm · Stok azalınca otomatik sipariş
{const s=pptx.addSlide();header(s,"Stok azalınca otomatik sipariş","Çözüm",36);
 const steps=["Stok azalır","Sistem sipariş taslağı hazırlar","Siz onaylarsınız","Tedarikçiye mesaj gider"];
 const sw=(W-2*M-3*0.45)/4;
 steps.forEach((t,i)=>{const x=M+i*(sw+0.45);card(s,x,1.9,sw,0.75,i===2?NAVY:WHITE,i===2?null:LINE);
  T(s,`${i+1}  ${t}`,{x:x+0.15,y:1.9,w:sw-0.3,h:0.75,fontSize:15,bold:true,color:i===2?WHITE:GREEN,align:"center",valign:"middle"});
  if(i<3)T(s,"➜",{x:x+sw,y:1.9,w:0.45,h:0.75,fontSize:20,bold:true,color:GREEN,align:"center",valign:"middle"});});
 const iy=3.3,ih=2.85,iw=4.55,pw=W-2*M-2*iw-0.4;
 label(s,"Stok ekranı: azalan ürünler",M,2.9,iw,GREEN);img(s,"stok.png",M,iy,iw,ih);
 label(s,"Tedarik ekranı: taslak, onay, gönderim",M+iw+0.2,2.9,iw,GREEN);img(s,"tedarik.png",M+iw+0.2,iy,iw,ih);
 const px=M+2*iw+0.4;label(s,"Tedarikçinin telefonu",px,2.9,pw,GREEN);
 const tel=path.join(IMG,"telegram-telefon.png");
 if(fs.existsSync(tel))img(s,"telegram-telefon.png",px,iy,pw,ih);
 else{card(s,px,iy,pw,ih,NAVY);card(s,px+0.15,iy+0.2,pw-0.3,ih-0.55,"1F3D52");
  T(s,"Merhaba Anadolu Güç Sistemleri, OtoHesap Demo Mağaza için sipariş talebi: Powerbank 20000 mAh × 63 adet. Tahmini tutar 69.300,00 ₺. Teslim süresi 3 gün. Onay için bu mesajı yanıtlayabilirsiniz. — OtoHesap",{x:px+0.27,y:iy+0.3,w:pw-0.54,h:ih-0.85,fontSize:10.5,color:WHITE,valign:"top"});
  T(s,"Telegram · 13 Eylül 21:19",{x:px+0.15,y:iy+ih-0.35,w:pw-0.3,h:0.3,fontSize:9,color:MB,align:"right"});}
 T(s,"Siz onaylamadan hiçbir mesaj gitmez.",{x:M,y:6.4,w:W-2*M,h:0.4,fontSize:14,bold:true,color:INK,align:"center"});
 s.addNotes("1:55–2:35. Stok azalınca sistem miktarı ve tutarı hesaplayıp taslağı hazırlar; kendi başına sipariş vermez. Siz onaylarsınız, mesaj tedarikçinin Telegram'ına düşer. Onaysız hiçbir mesaj gitmez.");}

// 6 · Ekip
{const s=pptx.addSlide();header(s,"Ekip","");
 const team=[["KY","Kutay Yıldırım"],["MA","Muratcan Ateş"],["ÖE","Ömer Faruk Eskitürk"]];
 team.forEach((t,i)=>{const w=(W-2*M-0.4)/3,x=M+i*(w+0.2);card(s,x,2.2,w,2.2,WHITE,LINE);
  s.addShape("ellipse",{x:x+w/2-0.45,y:2.5,w:0.9,h:0.9,fill:{color:GREEN},line:{type:"none"}});
  T(s,t[0],{x:x+w/2-0.45,y:2.5,w:0.9,h:0.9,fontSize:20,bold:true,color:WHITE,align:"center",valign:"middle"});
  T(s,t[1],{x:x+0.15,y:3.55,w:w-0.3,h:0.6,fontSize:17,bold:true,color:INK,align:"center",valign:"middle"});});
 T(s,"Medeniyet Teknopark · TeknoKampüs Arena",{x:M,y:4.8,w:W-2*M,h:0.45,fontSize:16,color:MUTED,align:"center"});
 T(s,"Sırada: pazaryeri siparişleri · e-belge · çok kullanıcılı sürüm",{x:M,y:5.7,w:W-2*M,h:0.5,fontSize:20,bold:true,color:GREEN,align:"center"});
 T(s,"github.com/Farukes/Oto-Hesap",{x:M,y:6.25,w:W-2*M,h:0.35,fontSize:13,color:MUTED,align:"center"});
 s.addNotes("2:35–2:55. İsimler. Sırada pazaryeri siparişleri ve e-belge. Teşekkürler.");}
pptx.writeFile({fileName:OUT}).then(()=>console.log("yazıldı:",OUT));
