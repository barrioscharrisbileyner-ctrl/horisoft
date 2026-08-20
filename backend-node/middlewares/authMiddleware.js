const jwt = require("jsonwebtoken");

const JWT_SECRET = process.env.JWT_SECRET;

/**
 * Middleware de autenticación.
 *
 * Espera el token en el header:
 *   Authorization: Bearer <token>
 *
 * - Si no hay header, o no tiene el formato "Bearer <token>": 401.
 * - Si el token existe pero es inválido, está mal firmado o expiró: 403.
 * - Si el token es válido: agrega el payload decodificado a req.usuario
 *   y deja pasar la petición con next().
 */
function verificarToken(req, res, next) {
    const authHeader = req.headers["authorization"];

    if (!authHeader) {
        return res.status(401).json({ mensaje: "Acceso denegado: token no proporcionado" });
    }

    const [esquema, token] = authHeader.split(" ");

    if (esquema !== "Bearer" || !token) {
        return res.status(401).json({
            mensaje: "Formato de token inválido. Use el header: Authorization: Bearer <token>",
        });
    }

    try {
        const payload = jwt.verify(token, JWT_SECRET);
        req.usuario = payload; // disponible para los controladores siguientes
        next();
    } catch (error) {
        return res.status(403).json({ mensaje: "Token inválido o expirado" });
    }
}

module.exports = verificarToken;
