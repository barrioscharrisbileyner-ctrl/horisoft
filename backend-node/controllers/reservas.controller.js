const reservasService = require("../services/reservas.service");

class ReservasController {

    listar(req, res) {
        // Soporta filtro opcional ?id_zona=1
        if (req.query.id_zona) {
            return res.json(reservasService.obtenerPorZona(req.query.id_zona));
        }
        res.json(reservasService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            const reserva = reservasService.obtenerPorId(req.params.id);
            res.json(reserva);
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            // Si el usuario autenticado pertenece a una residencia, se usa la del
            // token (no la del body): así un residente no puede reservar a nombre
            // de otra residencia. Un usuario sin residencia (ej. Administrador)
            // debe indicar id_residencia en el body.
            const datos = { ...req.body };
            if (req.usuario && req.usuario.id_residencia) {
                datos.id_residencia = req.usuario.id_residencia;
            }
            const reserva = reservasService.crear(datos);

            res.status(201).json({
                mensaje: "Reserva creada correctamente",
                reserva
            });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    cambiarEstado(req, res) {
        try {
            const reserva = reservasService.cambiarEstado(
                req.params.id,
                req.body.estado
            );
            res.json(reserva);
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            reservasService.eliminar(req.params.id);
            res.json({ mensaje: "Reserva eliminada" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new ReservasController();
