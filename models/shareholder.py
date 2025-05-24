from dataclasses import dataclass
from typing import Optional

@dataclass
class Shareholder:
    """Modèle pour représenter un actionnaire"""
    
    id: str
    nom: str
    prenom: str
    parts_sociales: int  # Nombre de parts sur 100 total
    email: Optional[str] = None
    telephone: Optional[str] = None
    actif: bool = True
    
    @property
    def pourcentage_actions(self) -> float:
        """Calcule le pourcentage basé sur les parts sociales"""
        return self.parts_sociales
    
    @property
    def valeur_parts(self) -> float:
        """Calcule la valeur en dollars des parts détenues"""
        return (self.parts_sociales / 100) * 150000
    
    def to_dict(self) -> dict:
        """Convertit l'actionnaire en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'parts_sociales': self.parts_sociales,
            'pourcentage_actions': self.pourcentage_actions,
            'email': self.email or '',
            'telephone': self.telephone or '',
            'actif': self.actif
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Shareholder':
        """Crée un actionnaire à partir d'un dictionnaire"""
        # Gestion de la rétrocompatibilité
        if 'parts_sociales' in data:
            parts_sociales = int(data['parts_sociales'])
        elif 'pourcentage_actions' in data:
            # Conversion depuis l'ancien format pourcentage vers parts sociales
            parts_sociales = int(data['pourcentage_actions'])
        else:
            parts_sociales = 1
            
        return cls(
            id=data['id'],
            nom=data['nom'],
            prenom=data['prenom'],
            parts_sociales=parts_sociales,
            email=data.get('email', None) if data.get('email') else None,
            telephone=data.get('telephone', None) if data.get('telephone') else None,
            actif=bool(data.get('actif', True))
        )
    
    def nom_complet(self) -> str:
        """Retourne le nom complet de l'actionnaire"""
        return f"{self.prenom} {self.nom}"
    
    def validate(self) -> bool:
        """Valide les données de l'actionnaire"""
        if not self.id or not self.nom or not self.prenom:
            return False
        if self.parts_sociales <= 0 or self.parts_sociales > 100:
            return False
        return True
    
    def calculer_part_benefice(self, benefice_total: float) -> float:
        """Calcule la part de bénéfice pour cet actionnaire"""
        return benefice_total * (self.pourcentage_actions / 100)
