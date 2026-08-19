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
            const reserva = reservasService.crear(req.body);

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
