-- Delete duplicate ContactType records created by init_contact_types command
-- Keep original records with icon prefixes
DELETE FROM dictionaries_contacttype WHERE id IN (5, 6, 7, 8);
