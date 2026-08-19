const visitantesService = require("../services/visitantes.service");

class VisitantesController {

    listar(req, res) {
        // Soporta filtro opcional ?estado=En instalación
        if (req.query.activas === "true") {
            return res.json(visitantesService.obtenerActivas());
        }
        res.json(visitantesService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            const visita = visitantesService.obtenerPorId(req.params.id);
            res.json(visita);
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    registrarIngreso(req, res) {
        try {
            const visita = visitantesService.registrarIngreso(req.body);

            res.status(201).json({
                mensaje: "Ingreso registrado correctamente",
                visita
            });
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    registrarSalida(req, res) {
        try {
            const visita = visitantesService.registrarSalida(req.params.id);
            res.json({
                mensaje: "Salida registrada correctamente",
                visita
            });
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            visitantesService.eliminar(req.params.id);
            res.json({ mensaje: "Registro de visita eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new VisitantesController();
