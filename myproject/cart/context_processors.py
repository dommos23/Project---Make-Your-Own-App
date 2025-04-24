def cart_processor(request):
    """Context processor to add cart information to all templates."""
    if request.user.is_authenticated:
        # Replace with your actual logic to get cart items
        cart_count = 0  # Placeholder
        return {'cart_count': cart_count}
    return {'cart_count': 0}  # Default for unauthenticated users