"""Explicit public-file boundary shared by builds and navigation checks."""
ARTICLE_ROUTES = ('articles', 'senior-personal-training', 'training-after-joint-replacement',
                  'golf-fitness-couples', 'parkinsons-exercise-scottsdale')
PUBLIC_ROUTES = ('', 'about-me', 'in-home-personal-training', 'semi-private-personal-training',
                 'virtual-personal-training', 'service-areas', 'pwr-moves', 'rates', 'testimonials',
                 'free-class-sign-up', 'recipes', 'privacy', 'forms', 'forms/client-information',
                 'forms/par-q', 'home', 'classes', 'client-information-form', 'par-q-form',
                 'apps/travel-planner', 'apps/travel-planner/privacy', *ARTICLE_ROUTES)
PUBLIC_FILES = ('404.html', 'google36fa4f5bebef5fcb.html', 'robots.txt', 'sitemap.xml', 'llms.txt',
                'favicon.ico', 'og-image.jpg', 'site.webmanifest', 'CNAME', '.nojekyll',
                'docs/liability-waiver.pdf', 'docs/late-cancel-policy.pdf')
ASSET_EXTENSIONS = {'.js', '.css', '.jpg', '.jpeg', '.png', '.svg', '.webp', '.gif', '.ico',
                    '.woff', '.woff2', '.ttf', '.mp4', '.webm'}


def public_files(root):
    files = {route + '/index.html' if route else 'index.html' for route in PUBLIC_ROUTES}
    files.update(PUBLIC_FILES)
    for path in (root / 'assets').rglob('*'):
        if path.is_symlink():
            raise ValueError('public assets must not contain symlinks: ' + str(path))
        if path.is_file() and not any(part.startswith('.') for part in path.relative_to(root).parts):
            if path.suffix.lower() in ASSET_EXTENSIONS:
                files.add(path.relative_to(root).as_posix())
    for rel in files:
        path = root / rel
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root.parent):
            raise ValueError('public files must not traverse symlinks: ' + rel)
        if not path.is_file():
            raise ValueError('required public file missing: ' + rel)
    return files
