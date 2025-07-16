import bcrypt

entered = "password1"
stored_hash = "$2b$12$CzM5tINRnBwjBIlvcayzTuKbrt35XfD8TidNKxg72PGP4WPODy232"  # from your DB

print(bcrypt.checkpw(entered.encode(), stored_hash.encode()))  # Should be True
