-- MySQL Workbench Forward Engineering
-- Este bloque inicial lo genera MySQL Workbench automático
-- Aquí solo guarda valores actuales, desactiva validaciones y pone modos seguros para hacer las tablas.

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;  
-- Desactiva revisiones de valores únicos temporalmente (para evitar errores al crear tablas)

SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
-- Desactiva revisiones de llaves foráneas temporalmente (útil para crear tablas en orden)

SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
-- Cambia el modo de SQL para asegurar que se cumplan reglas más estrictas.
-- Al final se regresará al modo original.

-- -----------------------------------------------------
-- Aquí empiza la base de datos
-- -----------------------------------------------------

CREATE SCHEMA IF NOT EXISTS `esquema_asesorias` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
-- Crea el esquema (como una carpeta donde estarán tus tablas) si no existe aún.
-- `utf8mb4` permite guardar emojis y todos los caracteres correctamente.

USE `esquema_asesorias` ;
-- Le decimos a MySQL que vamos a trabajar dentro de este esquema.

-- -----------------------------------------------------
-- Table `usuarios`
-- Aquí se almacenan datos de todos los usuarios del sistema: alumnos y tutores
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `esquema_asesorias`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,  
  -- ID único por cada usuario, se incrementa automáticamente.

  `nombre` VARCHAR(45) NOT NULL,  
  -- Primer nombre del usuario.

  `apellido` VARCHAR(45) NOT NULL,  
  -- Apellido del usuario.

  `email` VARCHAR(255) NOT NULL,  
  -- Correo del usuario. Se deja largo porque los correos pueden ser extensos.

  `contrasena` VARCHAR(255) NOT NULL,  
  -- La contraseña ya encriptada (por eso 255 caracteres).

  `es_tutor` TINYINT(1) NOT NULL DEFAULT 0,
  -- Campo que indica si el usuario es tutor.
  -- 0 = no tutor, 1 = tutor.

  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  -- Fecha automática de creación del registro.

  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  -- Fecha automática que cambia cada vez que se edita el registro.

  PRIMARY KEY (`id`))
  -- Se establece la llave primaria para identificar cada usuario.

ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
-- Configuración moderna y recomendada para tablas.

-- -----------------------------------------------------
-- Table `asesorias`
-- Tabla donde se registran todas las asesorías realizadas
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `esquema_asesorias`.`asesorias` (
  `id` INT NOT NULL AUTO_INCREMENT,
  -- Identificador único de la asesoría.

  `tema` VARCHAR(100) NOT NULL,
  -- Tema que se va a tratar en la asesoría.

  `fecha` DATE NOT NULL,
  -- Fecha en la que se programó la asesoría.

  `duracion` INT NOT NULL,
  -- Duración en minutos u otra unidad según tu sistema.

  `notas` TEXT NULL DEFAULT NULL,
  -- Notas adicionales (pueden ser largas, por eso TEXT).

  `usuario_id` INT NOT NULL,
  -- ID del usuario (alumno) que solicita la asesoría.

  `tutor_id` INT NULL DEFAULT NULL,
  -- ID del tutor asignado (puede ser NULL si aún no se asigna).

  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  -- Fecha de creación registrada automáticamente.

  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  -- Fecha que se actualiza automáticamente cuando se modifica algo.

  PRIMARY KEY (`id`),
  -- La llave principal es el id de la asesoría.

  INDEX `usuario_id` (`usuario_id` ASC) VISIBLE,
  -- Índice para que MySQL pueda buscar más rápido las asesorías de un usuario.

  INDEX `tutor_id` (`tutor_id` ASC) VISIBLE,
  -- Índice para buscar rápido asesorías por tutor.

  CONSTRAINT `asesorias_ibfk_1`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `esquema_asesorias`.`usuarios` (`id`)
    ON DELETE CASCADE,
  -- Llave foránea que conecta asesorías con usuarios (alumno).
  -- CASCADE: si borras al usuario, también se borran sus asesorías.

  CONSTRAINT `asesorias_ibfk_2`
    FOREIGN KEY (`tutor_id`)
    REFERENCES `esquema_asesorias`.`usuarios` (`id`)
    ON DELETE SET NULL)
  -- Llave foránea que conecta al tutor con la asesoría.
  -- SET NULL: si borras al tutor, la asesoría queda sin tutor pero no se elimina.

ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- Restaurando configuraciones originales que se habían apagado al principio
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
