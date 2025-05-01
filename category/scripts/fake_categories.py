import os
import random

import django
import requests
from django.core.files import File
from faker import Faker

from category.models import Category
from store.models import Product, ProductGallery, Variation

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greatKart.settings")
django.setup()

faker = Faker()

# Define categories with related product names
category_products = {
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sweater", "Dress"],
    "Accessories": ["Watch", "Belt", "Handbag", "Wallet", "Sunglasses"],
    "Electronics": ["Laptop", "Smartphone", "Tablet", "Camera", "Smartwatch"],
    "Home Appliances": [
        "Refrigerator",
        "Microwave",
        "Washing Machine",
        "Air Conditioner",
        "Vacuum Cleaner",
    ],
    "Footwear": ["Sneakers", "Boots", "Sandals", "Loafers", "Heels"],
}

variation_values = {
    "Size": ["Small", "Medium", "Large", "X-Large"],
    "Color": ["Red", "Blue", "Green", "Black", "White"],
}

import urllib.parse


def download_unsplash_image(search_term, save_path, default_image_url=None):
    """Downloads an image from Unsplash based on a search term or falls back to a default image."""
    try:
        # URL encode the search term
        search_term = urllib.parse.quote(search_term)

        # Build the Unsplash URL
        url = f"https://source.unsplash.com/random/{search_term}"

        response = requests.get(url, stream=True, allow_redirects=True)

        if response.status_code == 200:
            with open(save_path, "wb") as out_file:
                for chunk in response.iter_content(1024):
                    out_file.write(chunk)
            print(f"✅ Downloaded: {save_path}")
        else:
            print(f"❌ Failed to download {search_term}: Status {response.status_code}")
            if default_image_url:
                # If Unsplash fails, download a default image (set the default image URL)
                print(f"Using default image for {search_term}.")
                response = requests.get(
                    default_image_url, stream=True, allow_redirects=True
                )
                with open(save_path, "wb") as out_file:
                    for chunk in response.iter_content(1024):
                        out_file.write(chunk)
    except Exception as e:
        print(f"❌ Exception while downloading {search_term}: {e}")


def create_product_with_images(n):
    for _ in range(n):
        # Randomly pick a category
        category_name = random.choice(list(category_products.keys()))
        category, created = Category.objects.get_or_create(
            category_name=category_name,
            defaults={
                "slug": faker.slug(),
                "description": faker.sentence(nb_words=10),
            },
        )

        # Prepare category image
        category_image_name = f"{category_name.replace(' ', '_')}_category.jpg"
        category_image_path = os.path.join(
            "media/photos/categories", category_image_name
        )
        os.makedirs(os.path.dirname(category_image_path), exist_ok=True)

        if not os.path.exists(category_image_path):
            download_unsplash_image(
                category_name.replace(" ", "+"), category_image_path
            )

        if os.path.exists(category_image_path):
            with open(category_image_path, "rb") as img_file:
                category.cat_image.save(category_image_name, File(img_file), save=True)
        else:
            print(f"⚠️ Skipped uploading missing category image for {category_name}")

        # Randomly pick a product related to the category
        product_name = random.choice(category_products[category_name])

        # Create the product
        product = Product.objects.create(
            product_name=product_name,
            slug=faker.slug(),
            description=faker.sentence(nb_words=15),
            price=random.randint(50, 2000),
            stock=random.randint(5, 50),
            is_available=True,
            category=category,
        )

        # Prepare product image
        product_image_name = f"{product_name.replace(' ', '_')}_product.jpg"
        product_image_path = os.path.join("media/photos/products", product_image_name)
        os.makedirs(os.path.dirname(product_image_path), exist_ok=True)

        if not os.path.exists(product_image_path):
            download_unsplash_image(product_name.replace(" ", "+"), product_image_path)

        if os.path.exists(product_image_path):
            with open(product_image_path, "rb") as img_file:
                product.images.save(product_image_name, File(img_file), save=True)

        # Create Variations and ProductGallery
        for variation_category, variation_list in variation_values.items():
            for variation_value in variation_list:
                # Create variation entry
                Variation.objects.create(
                    product=product,
                    variation_category=variation_category,
                    variation_value=variation_value,
                    is_active=True,
                )

                # For gallery images, use the base product image if variation image download fails
                gallery_image_name = (
                    f"{product_name.replace(' ', '_')}_{variation_value}_gallery.jpg"
                )
                gallery_image_path = os.path.join(
                    "media/store/products", gallery_image_name
                )
                os.makedirs(os.path.dirname(gallery_image_path), exist_ok=True)

                if not os.path.exists(gallery_image_path):
                    # Try to download the gallery image for the variation (fallback to base product image)
                    variation_search_term = (
                        f"{product_name.replace(' ', '+')}+{variation_value}"
                    )
                    if not download_unsplash_image(
                        variation_search_term, gallery_image_path
                    ):
                        # If variation-specific image fails, use base product image
                        download_unsplash_image(
                            product_name.replace(" ", "+"), gallery_image_path
                        )

                if os.path.exists(gallery_image_path):
                    with open(gallery_image_path, "rb") as img_file:
                        ProductGallery.objects.create(
                            product=product,
                            image=File(img_file, name=gallery_image_name),
                        )

        print(
            f"🎯 Created product: {product_name} in category: {category_name} with variations and gallery images."
        )


# Example: Create 3 products
create_product_with_images(3)
