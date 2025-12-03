from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import bleach
from cryptography.fernet import Fernet, InvalidToken


# Helper to get a Fernet instance. Use BIO_ENCRYPTION_KEY env var if present.
def _load_fernet():
    key = os.environ.get('BIO_ENCRYPTION_KEY')
    if key:
        if isinstance(key, str):
            key = key.encode('utf-8')
        try:
            return Fernet(key)
        except Exception as exc:
            logging.warning('Invalid BIO_ENCRYPTION_KEY: %s', exc)
    # Fallback: generate a key (NOT recommended for production)
    logging.warning('No BIO_ENCRYPTION_KEY found in environment; generating temporary key (not persistent).')
    return Fernet(Fernet.generate_key())


FERNET = _load_fernet()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), default='user', nullable=False)
    # Keep a (deprecated) plain-text bio column for compatibility if present;
    # the application will use `bio_encrypted` via the `bio` property.
    bio_plain = db.Column('bio', db.String(500), nullable=True)
    bio_encrypted = db.Column(db.LargeBinary, nullable=True)

    def __init__(self, username, password=None, role='user', bio=''):
        self.username = username
        self.role = role
        # assign to property so it gets sanitized+encrypted
        if bio:
            self.bio = bio
        if password:
            self.set_password(password)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # --- Bio handling: sanitize then encrypt on write; decrypt on read ---
    def set_bio(self, plaintext_bio: str):
        """Sanitize user-provided biography with bleach and store encrypted bytes."""
        allowed_tags = ["b", "i", "u", "em", "strong", "a", "p", "ul", "ol", "li", "br"]
        allowed_attrs = {"a": ["href", "title"]}
        clean = bleach.clean(plaintext_bio or "", tags=allowed_tags, attributes=allowed_attrs)
        try:
            token = FERNET.encrypt(clean.encode('utf-8'))
        except Exception as exc:
            logging.exception('Failed to encrypt bio: %s', exc)
            raise
        self.bio_encrypted = token
        # keep a truncated plain preview for quick listing (escaped in templates)
        self.bio_plain = (clean[:497] + '...') if len(clean) > 500 else clean

    def get_bio(self) -> str:
        """Decrypt and return the sanitized biography string.

        Returns an empty string if no bio is stored or decryption fails.
        """
        if not self.bio_encrypted:
            return self.bio_plain or ''
        try:
            decrypted = FERNET.decrypt(self.bio_encrypted)
            return decrypted.decode('utf-8')
        except InvalidToken:
            logging.warning('Failed to decrypt bio for user %s: invalid token', self.username)
            return self.bio_plain or ''
        except Exception as exc:
            logging.exception('Unexpected error decrypting bio for user %s: %s', self.username, exc)
            return self.bio_plain or ''

    # Keep a property so existing code can access `user.bio` and get the decrypted value.
    @property
    def bio(self):
        return self.get_bio()

    @bio.setter
    def bio(self, plaintext):
        self.set_bio(plaintext)







