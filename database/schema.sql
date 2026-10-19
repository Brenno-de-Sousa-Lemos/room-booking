CREATE DATABASE IF NOT EXISTS room_booking
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE room_booking;

CREATE TABLE IF NOT EXISTS usuarios (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(120) NOT NULL,
  email         VARCHAR(150) NOT NULL UNIQUE,
  senha_hash    VARCHAR(255) NOT NULL,
  perfil        ENUM('ADMIN','PROFESSOR','ALUNO') NOT NULL,
  registro      VARCHAR(30) NULL COMMENT 'Matrícula (aluno) ou registro funcional (professor)',
  ativo         TINYINT(1) NOT NULL DEFAULT 1,
  criado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  excluido_em   DATETIME NULL
);

CREATE TABLE IF NOT EXISTS logs_auditoria (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id    INT NULL,
  usuario_nome  VARCHAR(120) NULL,
  acao          VARCHAR(30) NOT NULL COMMENT 'LOGIN, LOGIN_FALHA, CRIACAO, EDICAO, EXCLUSAO',
  entidade      VARCHAR(50) NOT NULL COMMENT 'Ex: usuarios, salas, reservas',
  entidade_id   INT NULL,
  sucesso       TINYINT(1) NOT NULL DEFAULT 1,
  ip_origem     VARCHAR(45) NULL,
  criado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS termos_aceite (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id       INT NOT NULL,
  termo_versao     VARCHAR(10) NOT NULL,
  politica_versao  VARCHAR(10) NOT NULL,
  aceito_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ip_origem        VARCHAR(45) NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS salas (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(100) NOT NULL,
  tipo          ENUM('SALA','AUDITORIO') NOT NULL DEFAULT 'SALA',
  capacidade    INT NOT NULL,
  localizacao   VARCHAR(150) NULL,
  ativo         TINYINT(1) NOT NULL DEFAULT 1,
  criado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  excluido_em   DATETIME NULL
);

CREATE TABLE IF NOT EXISTS reservas (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  sala_id         INT NOT NULL,
  professor_id    INT NOT NULL,
  titulo          VARCHAR(150) NOT NULL,
  descricao       TEXT NULL,
  inicio          DATETIME NOT NULL,
  fim             DATETIME NOT NULL,
  google_event_id VARCHAR(255) NULL,
  sincronizado    TINYINT(1) NOT NULL DEFAULT 0,
  criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  excluido_em     DATETIME NULL,
  FOREIGN KEY (sala_id) REFERENCES salas(id),
  FOREIGN KEY (professor_id) REFERENCES usuarios(id),
  INDEX idx_reservas_sala_periodo (sala_id, inicio, fim)
);