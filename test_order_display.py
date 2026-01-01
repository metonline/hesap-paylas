#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test - Grup Sipariş Gösterimi"""

group_members = {
    'Ahmet Yilmaz': [
        {'name': 'Adana Kebap', 'quantity': 2, 'price': 45, 'total': 90, 'type': 'personal', 'emoji': '🌶️', 'image': '', 'person': 'Ahmet Yilmaz'},
        {'name': 'Ayran', 'quantity': 1, 'price': 8, 'total': 8, 'type': 'shared', 'emoji': '🥛', 'image': '', 'person': 'Ahmet Yilmaz'},
    ],
    'Fatma Demir': [
        {'name': 'Çoban Salatası', 'quantity': 1, 'price': 20, 'total': 20, 'type': 'personal', 'emoji': '🥗', 'image': '', 'person': 'Fatma Demir'},
        {'name': 'Ayran', 'quantity': 1, 'price': 8, 'total': 8, 'type': 'shared', 'emoji': '🥛', 'image': '', 'person': 'Fatma Demir'},
    ],
    'Mehmet Şahin': [
        {'name': 'Urfa Kebap', 'quantity': 1, 'price': 50, 'total': 50, 'type': 'personal', 'emoji': '🔥', 'image': '', 'person': 'Mehmet Şahin'},
        {'name': 'Ayran', 'quantity': 1, 'price': 8, 'total': 8, 'type': 'shared', 'emoji': '🥛', 'image': '', 'person': 'Mehmet Şahin'},
    ]
}

print('='*80)
print('📋 TÜM SİPARİŞLER - GRUP ARASINDA GÖRÜNTÜLENECEK FORMAT')
print('='*80)

for person, orders in group_members.items():
    person_total = sum(o['total'] for o in orders)
    print(f'\n👤 {person}:')
    if orders:
        personal_orders = [o for o in orders if o['type'] == 'personal']
        shared_orders = [o for o in orders if o['type'] == 'shared']
        
        # Bireysel siparişler
        for i, order in enumerate(personal_orders, 1):
            emoji = order.get('emoji', '🍽️')
            print(f'   {i}. 🔸 {emoji} {order["name"]} ({int(order["quantity"])} adet) = {order["total"]:.2f} ₺')
        
        # Ortak siparişler
        for i, order in enumerate(shared_orders, 1):
            emoji = order.get('emoji', '🍽️')
            order_person = order.get('person', person)
            print(f'   {i}. 🔹 {emoji} {order["name"]} ({int(order["quantity"])} adet) - {order_person} ekledi')
        
        print(f'   {"-"*70}')
        print(f'   Toplam: {person_total:>10.2f} ₺')
    else:
        print('   (Sipariş yok)')

print('\n' + '='*80)
print('📊 ORTAK ÜRÜNLER ÖZETI')
print('='*80)

shared_items = {}
for person, orders in group_members.items():
    for order in orders:
        if order['type'] == 'shared':
            item_key = order['name']
            if item_key not in shared_items:
                shared_items[item_key] = {'emoji': order['emoji'], 'people': [], 'quantities': []}
            shared_items[item_key]['people'].append(order['person'])
            shared_items[item_key]['quantities'].append(order['quantity'])

for item_name, data in shared_items.items():
    emoji = data['emoji']
    people = ', '.join(data['people'])
    total_qty = sum(data['quantities'])
    print(f"\n🔹 {emoji} {item_name} ({total_qty} adet toplam)")
    print(f"   Kimlerin eklediği: {people}")
