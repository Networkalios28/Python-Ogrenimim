# 1-"Bmw, Mercedes, Opel, Mazda" elemanlarına sahip bir liste oluşturunuz.
araclar = ["Bmw", "Mercedes", "Opel", "Mazda"]
# 2-Liste Kaç elemanlıdır ?
print("araç sayısı:",len(araclar))
# 3-Listenin ilk ve son elemanı nedir ?
print("listenin ilk ve son elemanı:",araclar[1], araclar[-1])
# 4-Mazda değerini Toyota ile değiştirin.
sayi = araclar.index("Mazda")
araclar[sayi]="Toyota"
print(araclar)
# 5-Mercedes listenin bir elemanı mıdır ?
sorgu = "Mercedes" in araclar
print("Mercedes listenin elemanı mıdır? :",sorgu)
# 6-Listenin -2 indeksindeki değer nedir ?
print("Opel")
# 7-Listenin ilk 3 elemanını alın.
print("listenin ilk 3 elemanı:",araclar[:3])
# 8-Listenin son 2 elemanı yerine "Totoya" ve "Renault" değerlerini ekleyin.
araclar[-2:]=["Toyota", "Renult"]
# 9-Listenin üzerine "Audi" ve "Nissan" değerlerini ekleyin.
araclar.append("Audi")
araclar.append("Nissan")
# 10- Listenin son elemaninı silin.
araclar.pop()
print("son eleman Nissan silindi:", araclar)
# 11- Liste elemanlarını tersten yazdırınız.
print(araclar[::-1])
# 12- Aşağıdaki verileri bir liste içinde saklayınız.
    # studentA: Yiğit Bilgi 2010, (70,60,70)
    # studentB: Sena Turan 1999, (80,80,70)
    # studentC: Ahmet Turan 1998, (80,70,90)
studentA = ["Yigit","Bilgi", 2010, (70,60,70)]
studentB = ["Sena","Turan", 1999, (80,80,70)]
studentC = ["Ahmet","Turan", 1998, (80,70,90)]
liste = [studentA,studentB,studentC]
#13- Liste elemanlarını ekrana yazdırınız.
print(liste)
print(liste[1][3][2])

