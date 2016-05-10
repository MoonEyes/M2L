# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------#
# afficherLesSalles
#------------------------------------------------------------------------------------#
def afficherLesSalles():
    """
    Fournit à la vue HTML la liste de toutes les salles avec l'ensemble des informations
    """
    rowsSalles =db(db.salle.categorie_id==db.categorie.id).select(db.salle.capacite,db.categorie.nom,db.salle.id,db.salle.nom,db.categorie.heureOuverture,db.categorie.heureOuvertureMinutes) #requête permettant de récupérer les informations des salles
    trieSalles =db(db.salle.categorie_id==db.categorie.id).select(db.salle.capacite,db.categorie.nom,db.salle.id,db.salle.nom,db.categorie.heureOuverture,db.categorie.heureOuvertureMinutes, db.categorie.heureFermeture, db.categorie.heureFermetureMinutes, orderby=db.categorie.nom|~db.salle.capacite )#requête permettant de récupérer les informations des salles et les trier par capacité et catégorie
    
    return locals()

#------------------------------------------------------------------------------------#
# afficherSallesCategorie
#------------------------------------------------------------------------------------#
def afficherSallesCategorie():
    """
    Fournit à la vue la liste des salles dont la categorie a été transmise par l'URL dans la variable Select_categ
    """
    #recupération des varaibles transmises par la requête HTTP
    uneCategorie=request.vars.Select_categ

    # requête permettant de récupérer le nom de la catégorie précédemment sélectionnée
    rowCateg=db(db.categorie.id==uneCategorie).select(db.categorie.nom,orderby=db.categorie.nom)
    
    nomCateg=rowCateg[0].nom
    
    # requête permettant de sélectionner les salles de la catégorie précédemment sélectionnée
    rowsSalles =db((db.salle.categorie_id==uneCategorie==db.categorie.id)).select(db.salle.ALL,db.categorie.heureOuverture,db.categorie.heureOuvertureMinutes,db.categorie.heureFermeture,db.categorie.heureFermetureMinutes,db.categorie.nom, orderby=~db.salle.capacite)

    return locals()

#------------------------------------------------------------------------------------#
# ajouterSalle
#------------------------------------------------------------------------------------#
@auth.requires_login()
def ajouterSalle():
    """
    Fournit à la vue un formulaire d'ajout de salle
    """
    form=SQLFORM(db.salle)    #formulaire reposant sur la structure de la table Salle

    if form.process().accepted:
        # LE CODE PRESENT DANS CETTE SECTION SERA EXECUTÉ SEULEMENT APRÈS VALIDATION DU FORMULAIRE
        # on peut accéder aux valeurs renseignées dans les champs du formulaire grace à la variable : form.vars[nomChamp]

        response.flash='Nouvelle salle insérée'        # la salle est automatiquement ajoutée.


        redirect(URL('crtl_salle','afficherSallesCategorie',vars=dict(Select_categ=form.vars.categorie_id)))

    elif form.errors:
        response.flash='Erreurs de saisie'
  
    return locals()

#------------------------------------------------------------------------------------#
# demanderReservationSalle
#------------------------------------------------------------------------------------#
def demanderReservationSalle():
    """
    Fournit à la vue un formulaire de demande de réservation
    """

    #création du formulaire de reservation
    form = SQLFORM.factory(
        Field('DateDebut','datetime',requires=[IS_NOT_EMPTY(),IS_DATETIME(format=T('%d-%m-%Y %H:%M'),
                       error_message='doit être au format DD-MM-YYYY HH:MM!')]),
        Field('DateFin','datetime', requires=[IS_NOT_EMPTY(),IS_DATETIME(format=T('%d-%m-%Y %H:%M'),
                       error_message='doit être au format DD-MM-YYYY HH:MM!')]),
        Field('Categorie',db.categorie,requires=IS_IN_DB(db,db.categorie.id,'%(nom)s'))
        ,labels = {'DateDebut':'Date de début ','DateFin':'Date de fin ','NbParticipants':'Nombre de participants '})


    if form.validate():
        # Code exécuté à la validation du formulaire
        # redirection vers la page de sélection d'une salle disponible avec transmission des données du formulaire
        redirect(URL('ctrl_salle','rechercherSalleDisponible',vars=form.vars))

    elif form.errors:
        response.flash = 'Le formulaire contient des erreurs'

    return locals()

#------------------------------------------------------------------------------------#
# index
#------------------------------------------------------------------------------------#
def index():
    """
    Fournit à la vue la liste des catégories
    """
    rowsCateg =db().select(db.categorie.id,db.categorie.nom)    #requête permettant de récupérer les id et nom des catégories

    return locals()

#------------------------------------------------------------------------------------#
# modifierSalle
#------------------------------------------------------------------------------------#
@auth.requires_login()
def modifierSalle():
    """
    Fournit à la vue HTML un formulaire de modification d'une salle dont l'id est transmis par URL
    """
    idSalle = request.vars['salle']    # récupération des variables du formulaire transmises par la rêquete HTTP

    record = db.salle(idSalle) or redirect(URL('ctrl_salle','index'))
    form = SQLFORM(db.salle,record,deletable = False)

    if form.process().accepted:
        # LE CODE PRESENT DANS CETTE SECTION SERA EXECUTÉ SEULEMENT APRÈS VALIDATION DU FORMULAIRE
        # on peut accéder aux valeurs renseignées dans les champs du formulaire grace à la variable : form.vars[nomChamp]
        response.flash = 'Modification enregistrée'
        redirect(URL('ctrl_salle','afficherLesSalles'))

    elif form.errors:
        response.flash = 'Le formulaire contient des erreurs'

    return locals()


#------------------------------------------------------------------------------------#
# rechercherSalleDisponible
#------------------------------------------------------------------------------------#
def rechercherSalleDisponible():
    """
    Fournit à la vue la liste des salles disponibles à partir des données du formulaire de demande de réservation
    """
    # récupération des variables du formulaire transmises par la rêquete HTTP
    dateDebDdeR = request.vars['DateDebut']
    dateFinDdeR = request.vars['DateFin']
    categSalleRecherchee = request.vars['Categorie']


    #les salles disponibles sont :
    # celles qui appartiennent à la catégorie recherchée
    # qui ont des heures d'ouverture et de fermeture adaptés  
    # et qui sont libres pour la période de réservation demandée

    # réalisation d'une sous-requête : les salles qui sont libres pour la période de réservation demandée
    rowsSallesDispo1 = db((((db.reservation.dateDebut<dateDebDdeR) & (db.reservation.dateFin>dateDebDdeR))|((db.reservation.dateDebut<dateFinDdeR)&(db.reservation.dateFin>dateFinDdeR))))._select(db.reservation.salle_id)

    #rowsSallesDispo =db(~db.salle.id.belongs(rowsSallesDispo1)).select(db.salle.id,db.salle.nom,db.salle.capacite,distinct=True)
    rowsSallesDispo=db((~db.salle.id.belongs(rowsSallesDispo1))).select(db.salle.id,db.salle.nom,db.salle.capacite,distinct=True)

   
    return locals()

#------------------------------------------------------------------------------------#
# reserver
#------------------------------------------------------------------------------------#
def reserver():
    """
    Permet d'enregistrer la réservation.
    """
    # récupération des variables du formulaire transmises par la rêquete HTTP
    dateDebR = request.vars['dateDR']
    dateFinR = request.vars['dateFR']
    idSalleR = request.vars['salle']

    #insertion des données
    db.reservation.insert(dateDebut=dateDebR,dateFin=dateFinR,salle_id=idSalleR)
    # message de retour à afficher
    message = 'Votre réservation est enregistrée.'

    return locals()

#------------------------------------------------------------------------------------#
# visualiserReservation
#------------------------------------------------------------------------------------#
@auth.requires_login()
def visualiserReservation():
    """
    Fournit à la vue la liste des réservations correspondant à la date sélectionnée.
    """
    from datetime import datetime
    dateRecherchee = datetime.strptime(request.vars['date'],"%d-%m-%Y") # transformation en datetime de la chaine de caractère transmise via URL

    # requête de sélection des réservations correspondant à la date choisie
    rowsResa=db((((db.reservation.dateDebut.year() == dateRecherchee.year) & (db.reservation.dateDebut.day() == dateRecherchee.day) & (db.reservation.dateDebut.month() == dateRecherchee.month))|((db.reservation.dateFin.year() == dateRecherchee.year) & (db.reservation.dateFin.day() == dateRecherchee.day) & (db.reservation.dateFin.month() == dateRecherchee.month)))).select(db.reservation.ALL)
    
    return locals()
@auth.requires_login()
def visualiserReservation2():
    """
    Fournit à la vue la liste des réservations correspondant au nom sélectionnée.
    """
    idSalleR = request.vars['salle']

    # requête de sélection des réservations correspondant à la date choisie
    rowsResa=db(db.reservation.salle_id() == idSalleR).select(db.reservation.id, db.reservation.dateDebut, db.reservation.dateFin)
    
    return locals()