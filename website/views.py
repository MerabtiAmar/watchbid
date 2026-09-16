from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from . import db
import os
from datetime import datetime,date,timedelta
from sqlalchemy import and_, or_
from sqlalchemy import func

date_actuelle = date.today()


from .models import Watch, Bid, User
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    date_time = datetime
    time_delta = timedelta
    subquery = db.session.query(Bid.id_product, func.max(Bid.offer).label('max_offer')).group_by(Bid.id_product).subquery()
    produits = db.session.query(Watch, subquery.c.max_offer).join(subquery, Watch.id_watch == subquery.c.id_product).order_by(subquery.c.max_offer.desc()).limit(3)
    
    subquery_auctions = db.session.query(Bid.id_product, func.max(Bid.offer).label('max_offer')).group_by(Bid.id_product).subquery()
    auctions = db.session.query(Watch, subquery_auctions.c.max_offer).join(subquery_auctions, Watch.id_watch == subquery_auctions.c.id_product).filter(Watch.dateStart <= date_actuelle).order_by(Watch.dateEnd).limit(3).all()
    
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    return render_template("index.html", produits=produits,user=current_user,date=date_actuelle,auctions=auctions,categories=categories,datetime=date_time,timedelta=time_delta)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    if request.method == 'POST':
        # Récupérer les données soumises dans le formulaire
        full_name = request.form.get('name')
        email = request.form.get('email')
        tel = request.form.get('tel')

        method = request.form.get('_method')

        # Vérifier si la méthode de requête est PUT (mise à jour du profil)
        if method == 'PUT':
            user = User.query.get(current_user.id)

            # Mettre à jour les informations du profil uniquement si les champs sont remplis
            if full_name:
                user.full_name = full_name
            if email:
                # Vérifier si l'email est déjà utilisé par un autre utilisateur
                user_with_email = User.query.filter(User.email == email).first()
                if user_with_email and email != current_user.email:
                    flash('Cet email est déjà utilisé par un autre utilisateur.', 'error')
                    return redirect(url_for('views.profile'))
                user.email = email
            if tel:
                user.tel = tel

            # Sauvegarder les modifications dans la base de données
            db.session.commit()

            # Rediriger l'utilisateur vers la page de profil mise à jour
            flash('Profil mis à jour avec succès.', 'success')
            return redirect(url_for('views.profile'))

        # Vérifier si la méthode de requête est DELETE (suppression du profil)
        elif method == 'DELETE':
            user = User.query.get(current_user.id)

            # Supprimer l'utilisateur, ce qui entraînera la suppression en cascade des produits et des offres associées
            db.session.delete(user)
            db.session.commit()

            logout_user()
            flash('Votre profil et tous les produits associés ont été supprimés avec succès.', 'success')
            return redirect(url_for('views.home'))


    # Si la méthode est GET, afficher simplement la page de profil
    return render_template("view_profile.html", user=current_user,categories=categories)

from datetime import datetime

from datetime import datetime

@views.route('/offres-soumises', methods=['GET'])
@login_required
def offres_soumises():
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()

    offres_soumises = db.session.query(Bid.id_product, func.max(Bid.offer).label('max_offer')).filter_by(id_buyer=current_user.id).group_by(Bid.id_product).all()

    offres_max_autres_utilisateurs = db.session.query(Bid.id_product, func.max(Bid.offer).label('max_offer')).filter(Bid.id_product.in_([offre.id_product for offre in offres_soumises])).group_by(Bid.id_product).all()

    offres_max_autres_utilisateurs_dict = {offre.id_product: offre.max_offer for offre in offres_max_autres_utilisateurs}

    offres_details = []
    for offre in offres_soumises:
        produit = Watch.query.get(offre.id_product)
        jours_restants = (produit.dateEnd - date_actuelle).days
        offre_max_autres_utilisateurs = offres_max_autres_utilisateurs_dict.get(offre.id_product, 0)  # 0 par défaut si aucune offre maximale des autres utilisateurs
       
        # Ajouter les dates de début et de fin de l'offre à la liste offres_details
        offres_details.append({'id_produit': offre.id_product,
                               'nom_produit': produit.nom,
                               'offre': offre.max_offer,
                               'offre_max_autres_utilisateurs': offre_max_autres_utilisateurs,
                               'jours_restants': jours_restants,
                               'date_debut': produit.dateStart,
                               'date_fin': produit.dateEnd})

    return render_template("bid_historic.html", offres_details=offres_details, date_actuelle=date_actuelle, user=current_user,categories=categories)


@views.route('/my-products', methods=['GET', 'POST'])
@login_required
def mes_produits():
    if current_user.is_authenticated:
        produits = current_user.produits
        return render_template("view_products.html", user=current_user, produits=produits)



@views.route('/delete_product', methods=['POST'])
@login_required
def delete_product():
    if request.method == 'POST':
        # Récupérer l'ID du produit à supprimer depuis le formulaire
        product_id = request.form.get('id_product')

        # Rechercher le produit dans la base de données en fonction de son ID
        product = Watch.query.get(product_id)

        # Vérifier si le produit existe
        if product:
            # Vérifier si l'utilisateur actuel est bien le propriétaire du produit
            if product.user_id == current_user.id:
                # Supprimer le produit de la base de données
                db.session.delete(product)
                db.session.commit()
                flash('Votre produit a été supprimé avec succès.', 'success')
            else:
                flash('Vous n\'êtes pas autorisé à supprimer ce produit.', 'error')
        else:
            flash('Le produit que vous essayez de supprimer n\'existe pas.', 'error')

    # Rediriger vers la page de visualisation des produits de l'utilisateur
    return redirect(url_for('views.mes_produits'))




@views.route('/sellwatch', methods=['GET', 'POST'])
@login_required
def sellwatch():
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    if request.method == 'POST':
        nom = request.form.get('namewatch')
        marque = request.form.get('brand')
        categorie = request.form.get('category')
        annee = request.form.get('year')
        prix = request.form.get('price')
        start = datetime.strptime(request.form.get('start'), '%Y-%m-%d').date()
        end = datetime.strptime(request.form.get('end'), '%Y-%m-%d').date()
        desc = request.form.get('description')
        detail = request.form.get('details')
        img1 = save_image(request.files['image1'])
        img2 = save_image(request.files['image2'])
        img3 = save_image(request.files['image3'])

        watch = Watch.query.filter_by(nom=nom).first()


        if watch:
            flash('Watch already exists.', category='error')
        elif end < start:
            flash('Please check the dates are correct !', category='error')
        else:
            new_watch = Watch(nom=nom,
                              marque=marque,
                              categorie=categorie,
                              annee=annee,
                              prix=prix,
                              dateStart=start,
                              dateEnd=end,
                              desc=desc,
                              detail=detail,
                              img1=img1,
                              img2=img2,
                              img3=img3,
                              user_id=current_user.id)
            db.session.add(new_watch)
            db.session.commit()
            flash('Watch created!', category='success')
            return redirect(url_for("views.home"))

    return render_template("sellwatch.html", user=current_user,categories=categories)


@views.route('/shop-single', methods=['GET', 'POST'])
def info():
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    if request.method == 'POST':
        offer_price = float(request.form.get('offer-price'))
        product_id = int(request.args.get('id'))

        max_bid_price = db.session.query(func.max(Bid.offer)).filter(Bid.id_product == product_id).scalar()

        if max_bid_price is None or offer_price > max_bid_price:
            if current_user.is_authenticated:
                product = Watch.query.get(product_id)
                
                if product.user_id == current_user.id:
                    flash('Vous pouvez pas faire un offre sur votre produit !', category='error')
                else:
                    new_bid = Bid(id_product=product_id, id_buyer=current_user.id, offer=offer_price)

                    db.session.add(new_bid)
                    db.session.commit()

                    flash('Votre offre a été placée avec succès.', category='success')
            else:
                flash('Vous devez être connecté pour placer une offre.', category='error')
                return redirect(url_for('auth.login'))
        else:
            flash('Votre offre doit être strictement supérieure à l\'offre maximale actuelle.', category='error')

        return redirect(url_for('views.info', id=product_id))

    else:
        product_id = request.args.get('id')
        product = Watch.query.get(product_id)
        max_bid_price = db.session.query(func.max(Bid.offer)).filter(Bid.id_product == product_id).scalar()
        num_bids = db.session.query(func.count(Bid.id_bid)).filter(Bid.id_product == product_id).scalar()
        proprietaire = User.query.get(product.user_id)

        if not product:
            flash('Produit non trouvé.', category='error')
            return redirect(url_for('views.home'))

        details_list = product.detail.split('\n')

        return render_template("shop-single.html", product=product, details_list=details_list, user=current_user, date=date_actuelle, max_bid=max_bid_price, num_bids=num_bids,proprietaire=proprietaire,categories=categories)

    

@views.route('/shop', methods=['GET', 'POST'])
def shop():
    category = request.args.get('categorie')
    marque = request.args.get('marque')
    sort = request.args.get('sort')
    search  = request.args.get('search')

    if search:
        produits = Watch.query.filter(or_(Watch.nom.ilike(f'%{search}%'),Watch.marque.ilike(f'%{search}%'),Watch.categorie.ilike(f'%{search}%'))).all()
    elif category:
        produits = Watch.query.filter(Watch.categorie==category)
    elif marque:
        produits = Watch.query.filter(Watch.marque==marque)
    elif sort == "all":
        produits = Watch.query.all()
    elif sort == "populaires":
        subquery = db.session.query(Bid.id_product, func.count(Bid.id_bid).label('num_bids')).group_by(Bid.id_product).subquery()
        produits = db.session.query(Watch).join(subquery, Watch.id_watch == subquery.c.id_product).order_by(subquery.c.num_bids.desc()).all()
    elif sort == "terminees":
        duree_bientot_terminee = timedelta(days=2)
        date_limite = datetime.now() + duree_bientot_terminee
        produits = Watch.query.filter(Watch.dateEnd <= date_limite).order_by(Watch.dateEnd).all()

    elif sort == "prix-haut":
        subquery = db.session.query(Bid.id_product, func.max(Bid.offer).label('max_offer')).group_by(Bid.id_product).subquery()
        produits = db.session.query(Watch).join(subquery, Watch.id_watch == subquery.c.id_product).order_by(subquery.c.max_offer.desc()).all()
    elif sort == "prix-bas":
        subquery = db.session.query(Bid.id_product, func.max(Bid.offer).label('min_offer')).group_by(Bid.id_product).subquery()
        produits = db.session.query(Watch).join(subquery, Watch.id_watch == subquery.c.id_product).order_by(subquery.c.min_offer).all()    
    else:
        produits = Watch.query.all()
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    marques = Watch.query.with_entities(Watch.marque).distinct().all()
    return render_template("shop.html", produits=produits, user=current_user, date=date_actuelle, categories=categories,marques=marques)


@views.route('/about', methods=['GET'])
def about():
    categories = Watch.query.with_entities(Watch.categorie).distinct().all()
    return render_template("about.html",user=current_user,categories=categories)



def save_image(image):
    if image:
        filename = secure_filename(image.filename)
        filepath = os.path.join("website/assets/img", filename)
        image.save(filepath)
        return filename
    else:
        return None
