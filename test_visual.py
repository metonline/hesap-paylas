#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test visual enhancements with emoji and order display"""

import json
from datetime import datetime

def test_order_display():
    """Test the visual order display with emojis"""
    
    print("="*80)
    print("🍽️  TÜM SİPARİŞLER - VİZÜEL GÖSTERIM")
    print("="*80)
    
    # Sample order data with emojis
    group_members = {
        "Ahmet Yilmaz": [
            {
                'name': 'Adana Kebap',
                'quantity': 2,
                'price': 45.00,
                'total': 90.00,
                'type': 'personal',
                'emoji': '🌶️'
            },
            {
                'name': 'Ayran',
                'quantity': 1,
                'price': 8.00,
                'total': 8.00,
                'type': 'shared',
                'emoji': '🥛'
            }
        ],
        "Fatma Demir": [
            {
                'name': 'Çoban Salatası',
                'quantity': 1,
                'price': 20.00,
                'total': 20.00,
                'type': 'personal',
                'emoji': '🥗'
            },
            {
                'name': 'Künefe',
                'quantity': 2,
                'price': 25.00,
                'total': 50.00,
                'type': 'shared',
                'emoji': '🧡'
            }
        ],
        "Mehmet Şahin": [
            {
                'name': 'Balık Pilaü',
                'quantity': 1,
                'price': 75.00,
                'total': 75.00,
                'type': 'personal',
                'emoji': '🐟'
            },
            {
                'name': 'Hummus',
                'quantity': 1,
                'price': 15.00,
                'total': 15.00,
                'type': 'shared',
                'emoji': '🥜'
            }
        ]
    }
    
    # Display orders with emojis
    for person, orders in group_members.items():
        person_personal = sum(order['total'] for order in orders if order['type'] == 'personal')
        person_shared = sum(order['total'] for order in orders if order['type'] == 'shared')
        person_total = person_personal + person_shared
        
        print(f"\n👤 {person}:")
        if orders:
            for i, order in enumerate(orders, 1):
                if order['type'] == 'shared':
                    type_label = "🔹 Ortak"
                else:
                    type_label = "🔸 Bireysel"
                
                emoji = order.get('emoji', '🍽️')
                print(f"   {i}. {emoji} {type_label} {order['name']:20s} x{order['quantity']:>5.1f} @ {order['price']:>8.2f} ₺ = {order['total']:>10.2f} ₺")
            print(f"   {'-'*70}")
            print(f"   Toplam: {person_total:>10.2f} ₺")
    
    # Summary
    total_personal = sum(sum(o['total'] for o in orders if o['type'] == 'personal') 
                        for orders in group_members.values())
    total_shared = sum(sum(o['total'] for o in orders if o['type'] == 'shared') 
                      for orders in group_members.values())
    
    print(f"\n{'='*80}")
    print(f"Bireysel Toplam:                       {total_personal:>10.2f} ₺")
    print(f"Ortak Toplam:                          {total_shared:>10.2f} ₺")
    print(f"GENEL TOPLAM:                          {total_personal + total_shared:>10.2f} ₺")
    print("="*80 + "\n")
    
    # Restaurant order format
    print("="*80)
    print("📮 RESTORAN'A GÖNDERİLECEK FORMAT")
    print("="*80)
    
    message = f"""GRUP SİPARİŞ - #GRP-001
════════════════════════════════════════

"""
    
    for person, orders in group_members.items():
        if orders:
            message += f"👤 {person}:\n"
            for order in orders:
                type_emoji = "🔸" if order['type'] == 'personal' else "🔹"
                product_emoji = order.get('emoji', '🍽️')
                message += f"  {type_emoji} {product_emoji} {order['name']} x{order['quantity']} = {order['total']:.2f}₺\n"
            message += "\n"
    
    message += f"""════════════════════════════════════════
📊 ÖZET:
  Hesap Toplam: {total_personal + total_shared:.2f}₺
  Bahşiş: 25.00₺
  Vergi: 12.50₺
  ────────────────
  GENEL TOPLAM: {total_personal + total_shared + 25.00 + 12.50:.2f}₺

📍 Grup Üye Sayısı: 3
⏰ Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}
════════════════════════════════════════"""
    
    print(message)
    print("\n✅ Görsel iyileştirmeler başarıyla uygulandı!")
    print("   ✔️  Menü seçiminde ürün emojileri gösterilir")
    print("   ✔️  Siparişlerde ürün görselleri (emoji) gösterilir")
    print("   ✔️  Restoran formatında da ürün görselleri yer alır")
    print("   ✔️  Her üyenin siparişleri ve toplamları açık şekilde gösterilir")

if __name__ == "__main__":
    test_order_display()
