-- Esquema SQL representativo de los modelos Django del proyecto
CREATE TABLE core_hotel (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  timezone text NOT NULL DEFAULT 'America/Argentina/Buenos_Aires',
  checkin_time time NOT NULL DEFAULT '14:00',
  checkout_time time NOT NULL DEFAULT '10:00',
  google_review_url text NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL
);

CREATE TABLE core_room (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  code text NOT NULL,
  type text NULL,
  capacity integer NULL,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  UNIQUE (hotel_id, code)
);

CREATE TABLE core_reservation (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  room_id uuid NOT NULL REFERENCES core_room(id) ON DELETE CASCADE,
  guest_name text NOT NULL,
  guest_phone text NULL,
  guest_email text NULL,
  date_in date NOT NULL,
  date_out date NOT NULL,
  status text NOT NULL,
  source text NULL,
  notes text NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL
);

CREATE TABLE core_roomblock (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  room_id uuid NOT NULL REFERENCES core_room(id) ON DELETE CASCADE,
  date_in date NOT NULL,
  date_out date NOT NULL,
  reason text NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL
);

CREATE TABLE core_housekeepingtask (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  room_id uuid NOT NULL REFERENCES core_room(id) ON DELETE CASCADE,
  for_date date NOT NULL,
  status text NOT NULL,
  note text NULL,
  updated_at timestamptz NOT NULL,
  UNIQUE (hotel_id, room_id, for_date)
);

CREATE TABLE core_reviewrequest (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  reservation_id uuid NOT NULL REFERENCES core_reservation(id) ON DELETE CASCADE,
  channel text NOT NULL DEFAULT 'whatsapp_link',
  sent_at timestamptz NULL,
  status text NOT NULL DEFAULT 'pending',
  token text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
);

CREATE TABLE core_reviewresponse (
  id uuid PRIMARY KEY,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE,
  reservation_id uuid NOT NULL REFERENCES core_reservation(id) ON DELETE CASCADE,
  token text NOT NULL,
  score integer NOT NULL,
  feedback text NULL,
  routed_public boolean NOT NULL,
  created_at timestamptz NOT NULL
);

CREATE TABLE core_profile (
  id uuid PRIMARY KEY,
  user_id integer NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
  hotel_id uuid NOT NULL REFERENCES core_hotel(id) ON DELETE CASCADE
);
