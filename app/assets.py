from flask_assets import Bundle

def compile_assets(assets_env):
    """Configure and register asset bundles."""
    css_bundle = Bundle(
        'css/style.css',
        filters='cssmin',
        output='dist/main.css'
    )

    js_bundle = Bundle(
        'js/main.js',
        filters='jsmin',
        output='dist/main.js'
    )

    assets_env.register('css_all', css_bundle)
    assets_env.register('js_all', js_bundle)