SET CLIENT_ENCODING TO UTF8;
SET STANDARD_CONFORMING_STRINGS TO ON;
BEGIN;
CREATE TABLE "mfsdata"."patching" (gid serial,
"ptchlenght" int2,
"pthcdeptht" int2,
"descr" varchar(100),
"regdaterec" varchar(50),
"regdaterep" varchar(50),
"roadcarpet" varchar(50),
"geog" geography(POINT,4326));
ALTER TABLE "mfsdata"."patching" ADD PRIMARY KEY (gid);
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('3','5',NULL,'2012.07.23',NULL,'Асфальт','0101000020E6100000008CEB08F53F424040E85BE4B3704A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('5','5',NULL,'2012.07.23',NULL,'Асфальт','0101000020E6100000D8B6AFA37441424030E995A3E1704A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('20','10',NULL,'2012.07.23',NULL,'Бетон','0101000020E610000030B873EFCE424240B8BCB7910E714A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('100','15',NULL,'2012.07.23',NULL,'Щебень','0101000020E6100000A0D7C189743F4240B07E5B66476F4A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('1','2','3','4','5','Асфальт','0101000020E6100000C02807D4974242406847631A71724A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('15','15','Ямы','2012-07-31',NULL,'Щебень','0101000020E6100000D04696B5154E4240108AF72D84754A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('20','5','Ямы','2012-07-02',NULL,'Бетон','0101000020E6100000E0AD96B5B9404240B08D8E048A7D4A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('500','8','werwre','2012/08/02','2012/09/15','Асфальт','0101000020E610000098A395B5ECE04140204587D4357B4A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('35','5',NULL,NULL,NULL,'Бетон','0101000020E6100000E8F095B5175B4240D01873657D754A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('0','0',NULL,NULL,NULL,'Бетон','0101000020E6100000184B96359F26424080FB85B48C7F4A40');
INSERT INTO "mfsdata"."patching" ("ptchlenght","pthcdeptht","descr","regdaterec","regdaterep","roadcarpet",geog) VALUES ('0','0',NULL,NULL,NULL,'Щебень','0101000020E6100000804296358C1B4240A8B5E07A117E4A40');
CREATE INDEX "patching_geog_gist" ON "mfsdata"."patching" USING GIST ("geog");
COMMIT;
