use super::Token;
use std::fmt::Display;

impl Display for Token {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "<{}: ({}) '{}'>",
            self.token_type.clone(),
            self.pos_marker.clone().expect("PositionMarker unset"),
            self.raw.escape_debug(),
        )
    }
}
