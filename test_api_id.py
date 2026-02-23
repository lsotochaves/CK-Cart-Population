from cart import CartManager

cart = CartManager(None)  # no driver needed for this test
cart.load_from_file("Cards_to_add").preview().obtain_product_ids()

for card in cart.cards:
    print(f"  {card['url']} → {card.get('product_id')}")
