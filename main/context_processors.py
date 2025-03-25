def global_variables(request):
    return {
        'default_profile_picture': "https://res.cloudinary.com/dfohn9dcz/image/upload/v1742902918/default_profile.png",
        'site_name': "LifeXP",
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
        'player': request.user.player if request.user.is_authenticated else None,
        
    }