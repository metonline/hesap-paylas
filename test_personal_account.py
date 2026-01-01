#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test - Kişisel Hesap Özeti"""

import json

# Test verisi
group_members = {
    'Ahmet Yilmaz': [
        {'name': 'Adana Kebap', 'quantity': 2, 'price': 45, 'total': 90, 'type': 'personal', 'emoji': '🌶️', 'image': '', 'person': 'Ahmet Yilmaz'},
        {'name': 'Ayran', 'quantity': 1, 'price': 8, 'total': 8, 'type': 'shared', 'emoji': '🥛', 'image': '', 'person': 'Ahmet Yilmaz'},
    ],
    'Fatma Demir': [
        {'name': 'Çoban Salatası', 'quantity': 1, 'price': 20, 'total': 20, 'type': 'personal', 'emoji': '🥗', 'image': '', 'person': 'Fatma Demir'},
        {'name': 'Ayran', 'quantity': 1, 'price': 8, 'total': 8, 'type': 'shared', 'emoji': '🥛', 'image': '', 'person': 'Fatma Demir'},
    ]
}

# Hesaplamalar
total_personal = 110
total_shared = 16
num_people = 2
shared_per_person = total_shared / num_people
tip_amount = 25
tax_amount = 12.5
total_bill = total_personal + total_shared

print("="*80)
print("👤 KİŞİSEL HESAP ÖZETLERİ")
print("="*80)

for person, orders in group_members.items():
    person_personal = sum(o['total'] for o in orders if o['type'] == 'personal')
    person_consumption = person_personal + shared_per_person
    consumption_ratio = person_consumption / total_bill if total_bill > 0 else 0
    person_tip = tip_amount * consumption_ratio
    person_tax = tax_amount * consumption_ratio
    person_total = person_personal + shared_per_person + person_tip + person_tax
    
    print(f"\n{'='*80}")
    print(f"👤 {person} - KİŞİSEL HESABI")
    print(f"{'='*80}")
    
    # Ürün detayları
    print(f"\n📝 ÜRÜN DETAYLARı:")
    print(f"{'-'*80}")
    
    personal_items = [o for o in orders if o['type'] == 'personal']
    shared_items_set = [o for o in orders if o['type'] == 'shared']
    
    if personal_items:
        print(f"\n🔸 BİREYSEL SİPARİŞLER:")
        for item in personal_items:
            emoji = item.get('emoji', '🍽️')
            print(f"   {emoji} {item['name']:30s} x {int(item['quantity']):2d} adet @ {item['price']:>8.2f} ₺ = {item['total']:>10.2f} ₺")
        personal_subtotal = sum(item['total'] for item in personal_items)
        print(f"   {'-'*76}")
        print(f"   Bireysel Toplam:                                             {personal_subtotal:>10.2f} ₺")
    
    if shared_items_set:
        print(f"\n🔹 ORTAK SİPARİŞLER (PAYLAŞILAN):")
        print(f"   Ortak ürünlerin grup içinde eşit bölüşüm payı:")
        for item in shared_items_set:
            emoji = item.get('emoji', '🍽️')
            person_who_ordered = item.get('person', 'Bilinmeyen')
            print(f"   {emoji} {item['name']:30s} - {person_who_ordered} ekledi")
        print(f"   {'-'*76}")
        print(f"   Ortak Payı (Grup Toplamının 1/{num_people}'i):              {shared_per_person:>10.2f} ₺")
    
    # Adisyon detayları
    print(f"\n💰 ADİSYON DETAYLARI:")
    print(f"{'-'*80}")
    print(f"   Bireysel Tüketim:                                {person_personal:>10.2f} ₺")
    print(f"   Ortak Tüketim Payı:                              {shared_per_person:>10.2f} ₺")
    print(f"   ──────────────────────────────────────────────────────────")
    print(f"   Ara Toplam:                                      {person_personal + shared_per_person:>10.2f} ₺")
    
    if person_tip > 0:
        print(f"   Bahşiş ({consumption_ratio*100:.1f}% tüketim oranı):              {person_tip:>10.2f} ₺")
    
    if person_tax > 0:
        print(f"   Vergi ({consumption_ratio*100:.1f}% tüketim oranı):               {person_tax:>10.2f} ₺")
    
    print(f"   ──────────────────────────────────────────────────────────")
    print(f"   💳 GENEL TOPLAM (ÖDEYECEK TUTAR):               {person_total:>10.2f} ₺")
    print(f"   ══════════════════════════════════════════════════════════")

print("\n\n" + "="*80)
print("📌 AÇIKLAMALAR")
print("="*80)
print("""
1. BİREYSEL SİPARİŞLER: 
   Kişinin kendi seçtiği ve sadece o tüketecek ürünler.
   Bu tutarlar %100 o kişi öder.

2. ORTAK SİPARİŞLER:
   Grup üyelerinin birlikte tükettiği ürünler.
   Eşit şekilde bölüşülür (her kişi 1/N payı öder).

3. BAHŞİŞ DAĞILIMI:
   Bahşiş kişinin tüketim oranına göre dağıtılır.
   Yüksek tüketen daha fazla bahşiş öder.

4. VERGİ DAĞILIMI:
   Vergi de tüketim oranına göre dağıtılır.
   Her kişi kendi tüketimiyle orantılı vergi öder.

5. ÖDEYECEK TUTAR:
   Bireysel + Ortak Payı + Bahşiş Payı + Vergi Payı
""")
